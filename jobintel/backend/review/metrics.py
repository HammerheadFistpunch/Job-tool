"""Measured review-queue baseline statistics."""

from __future__ import annotations

from collections import Counter
from typing import Any


POSITIVE_LABELS = {"strong_match", "consider"}


def calculate_metrics(jobs: list[dict[str, Any]], cutoff: int = 10) -> dict[str, Any]:
    labels = Counter(job.get("match_label") for job in jobs if job.get("match_label"))
    states = Counter(job.get("review_state") or "new" for job in jobs)
    reasons = Counter(
        reason for job in jobs for reason in (job.get("reason_codes") or [])
    )
    reviewed = [job for job in jobs if job.get("match_label")]
    ranked_reviewed = [job for job in jobs[:cutoff] if job.get("match_label")]
    positive_top = sum(job["match_label"] in POSITIVE_LABELS for job in ranked_reviewed)
    hard_rejects = [job for job in reviewed if job["match_label"] == "hard_reject"]
    leaked = [job for job in hard_rejects if job.get("eligibility_status") != "ineligible"]
    return {
        "total_jobs": len(jobs),
        "reviewed_jobs": len(reviewed),
        "unreviewed_jobs": len(jobs) - len(reviewed),
        "review_coverage": len(reviewed) / len(jobs) if jobs else 0.0,
        "label_counts": dict(labels),
        "state_counts": dict(states),
        "reason_counts": dict(reasons.most_common()),
        "precision_at_cutoff": positive_top / len(ranked_reviewed) if ranked_reviewed else None,
        "precision_cutoff": cutoff,
        "precision_sample_size": len(ranked_reviewed),
        "hard_reject_count": len(hard_rejects),
        "hard_reject_leakage_count": len(leaked),
        "hard_reject_leakage_rate": len(leaked) / len(hard_rejects) if hard_rejects else None,
    }
