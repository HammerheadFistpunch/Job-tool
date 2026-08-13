"""Persistent job repository with source-aware deduplication."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from backend.storage.database import connect_database, initialize_database


REVIEW_STATES = {"new", "saved", "dismissed", "applied", "interviewed", "rejected"}
MATCH_LABELS = {"strong_match", "consider", "weak_match", "reject", "hard_reject"}


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


def _canonical_key(value: Any) -> str:
    url = str(value or "").strip()
    if not url:
        return ""
    try:
        parts = urlsplit(url)
        query = urlencode(sorted(
            (key, value) for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if not key.lower().startswith("utm_")
            and key.lower() not in {"ref", "referrer", "source"}
        ))
        return urlunsplit((
            parts.scheme.lower(), parts.netloc.lower(), parts.path.rstrip("/"), query, ""
        ))
    except ValueError:
        return url.lower().rstrip("/")


def _identity_part(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def _location_bucket(value: Any) -> str:
    location = _identity_part(value)
    if any(term in location for term in ("remote", "united states", "usa", "us only")):
        return "remote-us"
    if any(term in location for term in ("utah", "salt lake", "sandy", "lehi", "draper", "provo", "orem")):
        return "utah"
    return location


def _identity_key(job: dict[str, Any]) -> str:
    company = _identity_part(job.get("company"))
    title = _identity_part(job.get("title"))
    if not company or not title:
        return ""
    return "|".join((company, title, _location_bucket(job.get("location"))))


@dataclass
class UpsertSummary:
    fetched: int = 0
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    expired: int = 0


class JobStore:
    def __init__(self, database: str | Path | None = None):
        self.connection = connect_database(database)
        initialize_database(self.connection)
        self._backfill_discovery_identity()

    def _backfill_discovery_identity(self) -> None:
        """Upgrade existing jobs without replacing their IDs or review history."""
        rows = self.connection.execute(
            "SELECT * FROM jobs WHERE canonical_key IS NULL OR identity_key IS NULL"
        ).fetchall()
        for row in rows:
            job = dict(row)
            self.connection.execute(
                "UPDATE jobs SET canonical_key = ?, identity_key = ? WHERE id = ?",
                (_canonical_key(job.get("canonical_url")), _identity_key(job), row["id"]),
            )
        now = utc_now()
        self.connection.execute(
            """
            INSERT OR IGNORE INTO job_discoveries(
                job_id, source, external_id, scope, canonical_url, raw_json,
                first_seen_at, last_seen_at, active
            )
            SELECT id, lower(COALESCE(source, 'unknown')), COALESCE(external_id, ''),
                   lower(company), canonical_url, COALESCE(raw_json, '{}'),
                   COALESCE(first_seen_at, ?), COALESCE(last_seen_at, ?), active
            FROM jobs
            WHERE external_id IS NOT NULL AND external_id != ''
            """,
            (now, now),
        )
        self.connection.commit()

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

    def record_source_results(self, run_id: int, reports: list[dict[str, Any]]) -> None:
        self.connection.executemany(
            """
            INSERT INTO collection_source_results(
                run_id, source, company, status, fetched_count, accepted_count,
                filtered_count, expired_count, error, scope, query_name,
                query_json, location_scope, provider_count, rate_limit_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [(
                run_id, report.get("source", ""), report.get("company", ""),
                report.get("status", ""), report.get("fetched", 0),
                report.get("accepted", 0), report.get("filtered", 0),
                report.get("expired", 0), report.get("error", ""),
                report.get("scope", ""), report.get("query_name", ""),
                json.dumps(report.get("query_params", {}), sort_keys=True),
                report.get("location_scope", ""), report.get("provider_count", 0),
                json.dumps(report.get("rate_limit", {}), sort_keys=True),
            ) for report in reports],
        )
        self.connection.commit()

    def expire_missing_from_source(
        self, source: str, company: str, external_ids: list[str]
    ) -> int:
        """Expire one successful board/query scope without harming overlaps."""
        source_key = source.lower()
        scope_key = company.lower()
        affected = self.connection.execute(
            """
            SELECT DISTINCT j.id
            FROM jobs j JOIN job_discoveries d ON d.job_id = j.id
            WHERE j.active = 1 AND lower(d.source) = ? AND lower(d.scope) = ?
            """,
            (source_key, scope_key),
        ).fetchall()
        parameters: list[Any] = [source_key, scope_key]
        sql = """
            UPDATE job_discoveries SET active = 0
            WHERE active = 1 AND lower(source) = ? AND lower(scope) = ?
        """
        if external_ids:
            sql += f" AND external_id NOT IN ({','.join('?' for _ in external_ids)})"
            parameters.extend(external_ids)
        self.connection.execute(sql, parameters)
        self.connection.execute(
            """
            UPDATE jobs SET active = CASE WHEN EXISTS (
                SELECT 1 FROM job_discoveries d
                WHERE d.job_id = jobs.id AND d.active = 1
            ) THEN 1 ELSE 0 END
            """
        )
        self.connection.commit()
        return sum(
            1 for row in affected
            if not self.connection.execute(
                "SELECT active FROM jobs WHERE id = ?", (row["id"],)
            ).fetchone()["active"]
        )

    def list_source_health(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT csr.*, cr.started_at, cr.completed_at
            FROM collection_source_results csr
            JOIN collection_runs cr ON cr.id = csr.run_id
            WHERE csr.id IN (
                SELECT MAX(id) FROM collection_source_results GROUP BY source, scope
            )
            ORDER BY csr.company
            """
        ).fetchall()
        return [dict(row) for row in rows]

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
            scope = str(job.get("discovery_scope") or job.get("company") or "").strip().lower()
            canonical_key = _canonical_key(job.get("canonical_url") or job.get("source_url"))
            identity_key = _identity_key(job)
            digest = _content_hash(job)
            existing = self.connection.execute(
                """
                SELECT j.id, j.source, j.content_hash
                FROM job_discoveries d JOIN jobs j ON j.id = d.job_id
                WHERE d.source = ? AND d.external_id = ? AND d.scope = ?
                """,
                (source, external_id, scope),
            ).fetchone()
            if existing is None and (canonical_key or identity_key):
                existing = self.connection.execute(
                    """
                    SELECT id, source, content_hash FROM jobs
                    WHERE (? != '' AND canonical_key = ?)
                       OR (? != '' AND identity_key = ? AND source != ?)
                    ORDER BY CASE WHEN canonical_key = ? THEN 0 ELSE 1 END, id
                    LIMIT 1
                    """,
                    (
                        canonical_key, canonical_key, identity_key, identity_key,
                        source, canonical_key,
                    ),
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
                        , canonical_key, identity_key
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                    """,
                    (source, external_id, *values[:8], seen_at, *values[8:], canonical_key, identity_key),
                )
                job_id = int(self.connection.execute("SELECT last_insert_rowid()").fetchone()[0])
                summary.created += 1
            else:
                job_id = int(existing["id"])
                direct_sources = {"greenhouse", "lever"}
                should_refresh = source == existing["source"] or (
                    source in direct_sources and existing["source"] not in direct_sources
                )
                if existing["content_hash"] == digest or not should_refresh:
                    self.connection.execute(
                        "UPDATE jobs SET last_seen_at = ?, active = 1 WHERE id = ?",
                        (seen_at, job_id),
                    )
                    summary.unchanged += 1
                else:
                    self.connection.execute(
                        """
                        UPDATE jobs
                        SET source = ?, external_id = ?, company = ?, title = ?,
                            location = ?, description = ?, canonical_url = ?,
                            source_url = ?, posted_at = ?, updated_at = ?,
                            last_seen_at = ?, content_hash = ?, active = 1,
                            raw_json = ?, canonical_key = ?, identity_key = ?
                        WHERE id = ?
                        """,
                        (source, external_id, *values, canonical_key, identity_key, job_id),
                    )
                    summary.updated += 1

            self.connection.execute(
                """
                INSERT INTO job_discoveries(
                    job_id, source, external_id, scope, query_name, location_scope,
                    canonical_url, raw_json, first_seen_at, last_seen_at, active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ON CONFLICT(source, external_id, scope) DO UPDATE SET
                    job_id = excluded.job_id,
                    query_name = excluded.query_name,
                    location_scope = excluded.location_scope,
                    canonical_url = excluded.canonical_url,
                    raw_json = excluded.raw_json,
                    last_seen_at = excluded.last_seen_at,
                    active = 1
                """,
                (
                    job_id, source, external_id, scope,
                    str(job.get("query_name") or ""),
                    str(job.get("location_scope") or ""),
                    job.get("canonical_url") or job.get("source_url") or None,
                    json.dumps(job.get("raw") or job, ensure_ascii=False, default=str),
                    seen_at, seen_at,
                ),
            )

        self.connection.commit()
        return summary

    def list_active_jobs(self) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT id AS database_id, external_id AS id, source, company, title, location, description,
                   canonical_url, source_url, posted_at, updated_at
            FROM jobs WHERE active = 1
            ORDER BY last_seen_at DESC, id DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]

    def save_eligibility_evaluation(
        self, job_id: int, profile_version: str, decision: Any
    ) -> None:
        """Persist an explainable result without changing or deleting the job."""

        payload = decision.to_dict()
        job_row = self.connection.execute(
            "SELECT content_hash FROM jobs WHERE id = ?", (job_id,)
        ).fetchone()
        if job_row is None:
            raise KeyError(f"Job not found: {job_id}")
        self.connection.execute(
            """
            INSERT INTO job_eligibility_evaluations(
                job_id, profile_version, status, reasons_json, evaluated_at,
                job_content_hash
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id, profile_version) DO UPDATE SET
                status = excluded.status,
                reasons_json = excluded.reasons_json,
                evaluated_at = excluded.evaluated_at,
                job_content_hash = excluded.job_content_hash
            """,
            (
                job_id, profile_version, decision.status,
                json.dumps(payload["reasons"], ensure_ascii=False), utc_now(),
                job_row["content_hash"],
            ),
        )
        self.connection.commit()

    def list_eligibility_evaluations(self, profile_version: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT j.external_id, j.company, j.title, j.canonical_url,
                   e.status, e.reasons_json, e.evaluated_at
            FROM job_eligibility_evaluations e
            JOIN jobs j ON j.id = e.job_id
            WHERE e.profile_version = ?
            ORDER BY CASE e.status
                WHEN 'eligible' THEN 0 WHEN 'needs_review' THEN 1 ELSE 2 END,
                j.title
            """,
            (profile_version,),
        ).fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["reasons"] = json.loads(result.pop("reasons_json"))
            results.append(result)
        return results

    def save_review(
        self,
        job_id: int,
        review_state: str,
        match_label: str | None,
        reason_codes: list[str] | None = None,
        notes: str = "",
    ) -> dict[str, Any]:
        if review_state not in REVIEW_STATES:
            raise ValueError(f"Invalid review state: {review_state}")
        if match_label is not None and match_label not in MATCH_LABELS:
            raise ValueError(f"Invalid match label: {match_label}")
        if not self.connection.execute("SELECT 1 FROM jobs WHERE id = ?", (job_id,)).fetchone():
            raise KeyError(f"Job not found: {job_id}")

        self.connection.execute(
            """
            INSERT INTO job_reviews(
                job_id, review_state, match_label, reason_codes_json, notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id) DO UPDATE SET
                review_state = excluded.review_state,
                match_label = excluded.match_label,
                reason_codes_json = excluded.reason_codes_json,
                notes = excluded.notes,
                updated_at = excluded.updated_at
            """,
            (
                job_id, review_state, match_label,
                json.dumps(reason_codes or [], ensure_ascii=False), notes.strip(), utc_now(),
            ),
        )
        self.connection.commit()
        return self.get_review(job_id)

    def get_review(self, job_id: int) -> dict[str, Any]:
        row = self.connection.execute(
            "SELECT * FROM job_reviews WHERE job_id = ?", (job_id,)
        ).fetchone()
        if row is None:
            return {
                "job_id": job_id,
                "review_state": "new",
                "match_label": None,
                "reason_codes": [],
                "notes": "",
                "updated_at": None,
            }
        result = dict(row)
        result["reason_codes"] = json.loads(result.pop("reason_codes_json"))
        return result

    def list_review_queue(self, profile_version: str) -> list[dict[str, Any]]:
        rows = self.connection.execute(
            """
            SELECT j.id AS database_id, j.external_id, j.source, j.company, j.title,
                   j.location, j.description, j.canonical_url, j.posted_at,
                   j.similarity_score, e.status AS eligibility_status,
                   e.reasons_json AS eligibility_reasons_json, e.evaluated_at,
                   COALESCE(r.review_state, 'new') AS review_state,
                   r.match_label, COALESCE(r.reason_codes_json, '[]') AS reason_codes_json,
                   COALESCE(r.notes, '') AS notes, r.updated_at AS reviewed_at
            FROM jobs j
            JOIN job_eligibility_evaluations e
              ON e.job_id = j.id AND e.profile_version = ?
            LEFT JOIN job_reviews r ON r.job_id = j.id
            WHERE j.active = 1
            ORDER BY
              CASE COALESCE(r.review_state, 'new') WHEN 'new' THEN 0 WHEN 'saved' THEN 1 ELSE 2 END,
              CASE e.status WHEN 'eligible' THEN 0 WHEN 'needs_review' THEN 1 ELSE 2 END,
              j.last_seen_at DESC
            """,
            (profile_version,),
        ).fetchall()
        results = []
        for row in rows:
            result = dict(row)
            result["eligibility_reasons"] = json.loads(result.pop("eligibility_reasons_json"))
            result["reason_codes"] = json.loads(result.pop("reason_codes_json"))
            results.append(result)
        return results
