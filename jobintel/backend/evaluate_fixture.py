"""Validate deterministic policy against the reproducible baseline fixture."""

import json
from pathlib import Path

from backend.eligibility import EligibilityEvaluator
from backend.profile.loader import load_structured_profile


FIXTURE_PATH = Path("data/evaluation/baseline_jobs.json")


def evaluate_fixture(path: str | Path = FIXTURE_PATH) -> dict[str, object]:
    jobs = json.loads(Path(path).read_text(encoding="utf-8"))
    evaluator = EligibilityEvaluator(load_structured_profile())
    failures = []
    for job in jobs:
        actual = evaluator.evaluate(job).status
        if actual != job["expected_eligibility"]:
            failures.append({"id": job["id"], "expected": job["expected_eligibility"], "actual": actual})
    return {"total": len(jobs), "passed": len(jobs) - len(failures), "failures": failures}


if __name__ == "__main__":
    result = evaluate_fixture()
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["failures"] else 0)
