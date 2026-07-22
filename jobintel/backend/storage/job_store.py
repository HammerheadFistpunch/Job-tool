"""Persistent job repository with source-aware deduplication."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from backend.storage.database import connect_database, initialize_database


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _stable_external_id(job: dict[str, Any]) -> str:
    supplied = str(job.get("external_id") or job.get("id") or "").strip()
    if supplied:
        return supplied

    identity = "|".join(
        str(job.get(field) or "").strip().lower()
        for field in ("source", "canonical_url", "company", "title", "location")
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]


def _content_hash(job: dict[str, Any]) -> str:
    content = {
        key: job.get(key) or ""
        for key in (
            "title",
            "company",
            "location",
            "description",
            "canonical_url",
            "posted_at",
            "updated_at",
        )
    }
    serialized = json.dumps(content, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class UpsertSummary:
    fetched: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0


class JobStore:
    def __init__(self, database: str | Path | None = None):
        self.connection = connect_database(database)
        initialize_database(self.connection)

    def close(self) -> None:
        self.connection.close()

    def __enter__(self) -> "JobStore":
        return self

    def __exit__(self, *_args) -> None:
        self.close()

    def start_collection_run(self) -> int:
        cursor = self.connection.execute(
            "INSERT INTO collection_runs(started_at) VALUES (?)", (utc_now(),)
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def finish_collection_run(
        self,
        run_id: int,
        summary: UpsertSummary,
        errors: list[dict[str, str]] | None = None,
    ) -> None:
        errors = errors or []
        status = "completed" if not errors else "completed_with_errors"
        self.connection.execute(
            """
            UPDATE collection_runs
            SET completed_at = ?, status = ?, fetched_count = ?, new_count = ?,
                updated_count = ?, unchanged_count = ?, error_count = ?, errors_json = ?
            WHERE id = ?
            """,
            (
                utc_now(), status, summary.fetched, summary.created,
                summary.updated, summary.unchanged, len(errors),
                json.dumps(errors, ensure_ascii=False), run_id,
            ),
        )
        self.connection.commit()

    def fail_collection_run(self, run_id: int, error: Exception) -> None:
        self.connection.execute(
            """
            UPDATE collection_runs
            SET completed_at = ?, status = 'failed', error_count = 1, errors_json = ?
            WHERE id = ?
            """,
            (utc_now(), json.dumps([{"error": str(error)}]), run_id),
        )
        self.connection.commit()

    def upsert_jobs(self, jobs: Iterable[dict[str, Any]]) -> UpsertSummary:
        summary = UpsertSummary()
        seen_at = utc_now()

        for incoming in jobs:
            summary.fetched += 1
            job = dict(incoming)
            source = str(job.get("source") or "unknown").strip().lower()
            external_id = _stable_external_id(job)
            digest = _content_hash(job)
            existing = self.connection.execute(
                "SELECT id, content_hash FROM jobs WHERE source = ? AND external_id = ?",
                (source, external_id),
            ).fetchone()

            values = (
                str(job.get("company") or ""),
                str(job.get("title") or ""),
                str(job.get("location") or ""),
                str(job.get("description") or ""),
                job.get("canonical_url") or job.get("source_url") or None,
                job.get("canonical_url") or job.get("source_url") or None,
                job.get("posted_at") or None,
                job.get("updated_at") or None,
                seen_at,
                digest,
                json.dumps(job.get("raw") or job, ensure_ascii=False, default=str),
            )

            if existing is None:
                self.connection.execute(
                    """
                    INSERT INTO jobs(
                        source, external_id, company, title, location, description,
                        canonical_url, source_url, posted_at, updated_at,
                        first_seen_at, last_seen_at, content_hash, active, raw_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (source, external_id, *values[:8], seen_at, *values[8:]),
                )
                summary.created += 1
            elif existing["content_hash"] == digest:
                self.connection.execute(
                    "UPDATE jobs SET last_seen_at = ?, active = 1 WHERE id = ?",
                    (seen_at, existing["id"]),
                )
                summary.unchanged += 1
            else:
                self.connection.execute(
                    """
                    UPDATE jobs
                    SET company = ?, title = ?, location = ?, description = ?,
                        canonical_url = ?, source_url = ?, posted_at = ?, updated_at = ?,
                        last_seen_at = ?, content_hash = ?, active = 1, raw_json = ?
                    WHERE id = ?
                    """,
                    (*values, existing["id"]),
                )
                summary.updated += 1

        self.connection.commit()
        return summary

    def list_active_jobs(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT external_id AS id, source, company, title, location, description,
                   canonical_url, source_url, posted_at, updated_at
            FROM jobs WHERE active = 1
            ORDER BY last_seen_at DESC, id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]

