"""Evaluate stored jobs against the structured profile without loading AI."""

from backend.eligibility import EligibilityEvaluator
from backend.profile.loader import load_structured_profile
from backend.storage.job_store import JobStore


def run() -> None:
    profile = load_structured_profile()
    evaluator = EligibilityEvaluator(profile)
    counts = {"eligible": 0, "needs_review": 0, "ineligible": 0}

    with JobStore() as store:
        for job in store.list_active_jobs():
            decision = evaluator.evaluate(job)
            store.save_eligibility_evaluation(job["database_id"], profile.profile_version, decision)
            counts[decision.status] += 1

    print(
        "Eligibility evaluation complete | "
        f"eligible: {counts['eligible']} | needs review: {counts['needs_review']} | "
        f"ineligible: {counts['ineligible']}"
    )


if __name__ == "__main__":
    run()
