import tempfile
import unittest
from pathlib import Path

from backend.eligibility import EligibilityEvaluator
from backend.profile.loader import load_structured_profile
from backend.review import ReviewQueueService
from backend.storage.job_store import JobStore


PROFILE_PATH = Path("data/input/Profiles/patrick_profile.json")


class ReviewQueueTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "review.db"
        with JobStore(self.database) as store:
            store.upsert_jobs([{
                "external_id": "job-1",
                "source": "test",
                "company": "Builder Company",
                "title": "Technical Product Marketing Manager",
                "location": "Remote - US",
                "description": "Base salary: $100,000-$125,000. Lead positioning.",
                "canonical_url": "https://example.test/job-1",
            }])
        self.service = ReviewQueueService(self.database, PROFILE_PATH)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_queue_evaluates_missing_jobs_and_exposes_explanations(self):
        jobs = self.service.list_jobs()

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["eligibility_status"], "eligible")
        self.assertEqual(jobs[0]["review_state"], "new")
        self.assertTrue(jobs[0]["eligibility_reasons"])

    def test_review_state_label_and_notes_persist(self):
        job = self.service.list_jobs()[0]
        self.service.save_review(
            job["database_id"], "saved", "strong_match", ["responsibilities_fit"],
            "Good technical translation fit.",
        )

        reviewed = self.service.list_jobs()[0]
        self.assertEqual(reviewed["review_state"], "saved")
        self.assertEqual(reviewed["match_label"], "strong_match")
        self.assertEqual(reviewed["reason_codes"], ["responsibilities_fit"])
        self.assertEqual(reviewed["notes"], "Good technical translation fit.")

    def test_invalid_review_values_are_rejected(self):
        job = self.service.list_jobs()[0]
        with self.assertRaises(ValueError):
            self.service.save_review(job["database_id"], "maybe", None, [], "")

    def test_changed_posting_is_reevaluated_for_same_profile(self):
        job = self.service.list_jobs()[0]
        with JobStore(self.database) as store:
            store.upsert_jobs([{
                "external_id": "job-1",
                "source": "test",
                "company": "Builder Company",
                "title": "Technical Product Marketing Manager",
                "location": "Remote - US",
                "description": "Base salary: $50,000-$65,000.",
                "canonical_url": "https://example.test/job-1",
            }])

        refreshed = self.service.list_jobs()[0]
        self.assertEqual(refreshed["database_id"], job["database_id"])
        self.assertEqual(refreshed["eligibility_status"], "ineligible")
        self.assertIn(
            "salary_below_floor",
            [reason["code"] for reason in refreshed["eligibility_reasons"]],
        )

    def test_new_profile_version_creates_fresh_evaluation(self):
        profile = load_structured_profile(PROFILE_PATH)
        with JobStore(self.database) as store:
            job = store.list_active_jobs()[0]
            decision = EligibilityEvaluator(profile).evaluate(job)
            store.save_eligibility_evaluation(
                job["database_id"], "2026-08-12.1", decision
            )

        self.service.list_jobs()
        with JobStore(self.database) as store:
            versions = {
                row["profile_version"] for row in store.connection.execute(
                    "SELECT profile_version FROM job_eligibility_evaluations"
                )
            }
        self.assertEqual(versions, {"2026-08-12.1", "2026-08-12.2"})


if __name__ == "__main__":
    unittest.main()
