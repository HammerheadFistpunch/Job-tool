"""Measure JobIntel discovery against user-confirmed scheduled-task candidates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from backend.storage.job_store import JobStore


POSITIVE_LABELS = {"strong_match", "consider"}


def _hours_between(start: str | None, end: str | None) -> float | None:
    if not start or not end:
        return None
    try:
        started = datetime.fromisoformat(start.replace("Z", "+00:00"))
        ended = datetime.fromisoformat(end.replace("Z", "+00:00"))
        return round((ended - started).total_seconds() / 3600, 2)
    except (TypeError, ValueError):
        return None


def build_benchmark_report(database: str | Path | None = None) -> dict[str, Any]:
    """Return distinct benchmark candidates and confirmed-positive recall."""

    with JobStore(database) as store:
        candidates = store.connection.execute(
            """
            SELECT j.id AS job_id, j.company, j.title, j.canonical_url, j.active,
                   b.task_id, b.task_run_id, b.reported_at,
                   COALESCE(r.review_state, 'new') AS review_state,
                   r.match_label
            FROM jobs j
            JOIN benchmark_candidates b ON b.id = (
                SELECT b2.id FROM benchmark_candidates b2
                WHERE b2.job_id = j.id
                ORDER BY b2.reported_at DESC, b2.id DESC
                LIMIT 1
            )
            LEFT JOIN job_reviews r ON r.job_id = j.id
            ORDER BY b.reported_at DESC, j.company, j.title
            """
        ).fetchall()

        details = []
        for candidate in candidates:
            discoveries = store.connection.execute(
                """
                SELECT source, scope, first_seen_at, last_seen_at, active
                FROM job_discoveries
                WHERE job_id = ? AND source != 'scheduled_task'
                ORDER BY first_seen_at, source, scope
                """,
                (candidate["job_id"],),
            ).fetchall()
            first_independent = discoveries[0]["first_seen_at"] if discoveries else None
            label = candidate["match_label"]
            details.append({
                **dict(candidate),
                "confirmed_positive": label in POSITIVE_LABELS,
                "independently_discovered": bool(discoveries),
                "independent_sources": sorted({row["source"] for row in discoveries}),
                "independent_discoveries": [dict(row) for row in discoveries],
                "discovery_lag_hours": _hours_between(
                    candidate["reported_at"], first_independent
                ),
            })

    confirmed = [item for item in details if item["confirmed_positive"]]
    independently_found = [item for item in confirmed if item["independently_discovered"]]
    reviewed_non_positive = [
        item for item in details
        if item["match_label"] is not None and not item["confirmed_positive"]
    ]
    pending = [item for item in details if item["match_label"] is None]
    return {
        "report_version": "1.0",
        "benchmark_candidates": len(details),
        "confirmed_positive": len(confirmed),
        "reviewed_non_positive": len(reviewed_non_positive),
        "pending_review": len(pending),
        "independently_discovered_confirmed": len(independently_found),
        "confirmed_discovery_recall": (
            round(len(independently_found) / len(confirmed), 4) if confirmed else None
        ),
        "missed_confirmed_jobs": [
            {
                "job_id": item["job_id"],
                "company": item["company"],
                "title": item["title"],
                "canonical_url": item["canonical_url"],
            }
            for item in confirmed if not item["independently_discovered"]
        ],
        "candidates": details,
    }
