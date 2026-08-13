"""Keeps the review queue evaluated against the active profile version."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.eligibility import EligibilityEvaluator
from backend.config import load_settings
from backend.profile.loader import load_structured_profile
from backend.storage.job_store import JobStore


class ReviewQueueService:
    def __init__(
        self,
        database: str | Path | None = None,
        profile_path: str | Path | None = None,
    ):
        self.database = database
        self.profile = load_structured_profile(profile_path)
        self.evaluator = EligibilityEvaluator(self.profile)

    def refresh(self) -> dict[str, int]:
        """Evaluate jobs missing a result for the active profile version."""

        counts = {"evaluated": 0, "current": 0}
        with JobStore(self.database) as store:
            current_evaluations = {
                row["job_id"] for row in store.connection.execute(
                    """
                    SELECT e.job_id
                    FROM job_eligibility_evaluations e
                    JOIN jobs j ON j.id = e.job_id
                    WHERE e.profile_version = ?
                      AND e.job_content_hash = j.content_hash
                    """,
                    (self.profile.profile_version,),
                )
            }
            for job in store.list_active_jobs():
                if job["database_id"] in current_evaluations:
                    counts["current"] += 1
                    continue
                decision = self.evaluator.evaluate(job)
                store.save_eligibility_evaluation(
                    job["database_id"], self.profile.profile_version, decision
                )
                counts["evaluated"] += 1
        return counts

    def list_jobs(self) -> list[dict[str, Any]]:
        self.refresh()
        with JobStore(self.database) as store:
            jobs = store.list_review_queue(self.profile.profile_version)
        cap = int(load_settings().get("review_queue", {}).get("max_new_reviewable_per_employer", 0))
        if cap <= 0:
            return jobs
        counts: dict[str, int] = {}
        visible = []
        for job in jobs:
            if (
                job["review_state"] != "new"
                or job["eligibility_status"] == "ineligible"
                or job.get("benchmark_candidate")
            ):
                visible.append(job)
                continue
            company = str(job.get("company") or "Unknown").strip().lower()
            counts[company] = counts.get(company, 0) + 1
            if counts[company] <= cap:
                visible.append(job)
        return visible

    def save_review(
        self,
        job_id: int,
        review_state: str,
        match_label: str | None,
        reason_codes: list[str] | None,
        notes: str,
    ) -> dict[str, Any]:
        with JobStore(self.database) as store:
            return store.save_review(
                job_id, review_state, match_label, reason_codes, notes
            )
