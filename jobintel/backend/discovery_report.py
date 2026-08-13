"""Report whether the current database meets broad-discovery acceptance criteria."""

from __future__ import annotations

import json
from collections import Counter

from backend.review import ReviewQueueService
from backend.storage.job_store import JobStore


def build_report(database=None) -> dict:
    visible_jobs = ReviewQueueService(database).list_jobs()
    reviewable = [job for job in visible_jobs if job["eligibility_status"] != "ineligible"]
    employers = Counter(str(job.get("company") or "Unknown") for job in reviewable)

    with JobStore(database) as store:
        active_employers = store.connection.execute(
            "SELECT COUNT(DISTINCT lower(company)) FROM jobs WHERE active = 1"
        ).fetchone()[0]
        latest_run = store.connection.execute(
            "SELECT MAX(id) FROM collection_runs WHERE status != 'running'"
        ).fetchone()[0]
        query_rows = store.connection.execute(
            """
            SELECT source, scope, query_name, location_scope, status,
                   provider_count, fetched_count, accepted_count, filtered_count,
                   error, rate_limit_json
            FROM collection_source_results
            WHERE run_id = ? AND query_name != ''
            ORDER BY source, query_name
            """,
            (latest_run,),
        ).fetchall() if latest_run else []

    largest_company, largest_count = employers.most_common(1)[0] if employers else (None, 0)
    largest_share = largest_count / len(reviewable) if reviewable else 0
    scopes = {row["location_scope"] for row in query_rows}
    checks = {
        "at_least_15_employers": active_employers >= 15,
        "largest_employer_at_most_20_percent": largest_share <= 0.20,
        "at_least_30_reviewable_jobs": len(reviewable) >= 30,
        "remote_us_reported": "remote_us" in scopes,
        "utah_area_reported": "utah_area" in scopes,
        "all_queries_reported": bool(query_rows) and all(row["status"] in {"success", "failed"} for row in query_rows),
    }
    return {
        "passes": all(checks.values()),
        "checks": checks,
        "active_employers": active_employers,
        "reviewable_jobs": len(reviewable),
        "reviewable_employers": len(employers),
        "largest_employer": largest_company,
        "largest_employer_count": largest_count,
        "largest_employer_share": round(largest_share, 4),
        "query_reports": [dict(row) for row in query_rows],
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2))
    return 0 if report["passes"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
