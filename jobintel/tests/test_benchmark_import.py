import tempfile
import unittest
from pathlib import Path

from backend.benchmark import (
    BenchmarkImporter,
    BenchmarkImportError,
    build_benchmark_report,
)
from backend.review import ReviewQueueService
from backend.storage.job_store import JobStore


PROFILE_PATH = Path("data/input/Profiles/patrick_profile.json")


def benchmark_payload():
    return {
        "task_id": "6a71342630608191bd0f7e426f17ccbb",
        "task_name": "High-fit leadership jobs",
        "task_run_id": "2026-08-13T08:00:00-06:00",
        "reported_at": "2026-08-13T08:05:00-06:00",
        "jobs": [{
            "title": "Director of Technical Marketing",
            "company": "Builder Company",
            "location": "Remote - US",
            "description": "Base salary: $110,000-$130,000. Translate complex products.",
            "canonical_url": "https://jobs.example.test/director-technical-marketing",
            "selection_rationale": "Strong technical translation and leadership alignment.",
            "fit_signals": ["Technical marketing", "Cross-functional leadership"],
            "concerns": ["Travel percentage not listed"],
        }],
    }


class BenchmarkImporterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "benchmark.db"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_import_preserves_rationale_without_assigning_positive_label(self):
        result = BenchmarkImporter(self.database).import_payload(benchmark_payload())

        self.assertEqual(result["created"], 1)
        jobs = ReviewQueueService(self.database, PROFILE_PATH).list_jobs()
        self.assertEqual(len(jobs), 1)
        self.assertTrue(jobs[0]["benchmark_candidate"])
        self.assertEqual(
            jobs[0]["benchmark_rationale"],
            "Strong technical translation and leadership alignment.",
        )
        self.assertEqual(jobs[0]["benchmark_fit_signals"], [
            "Technical marketing", "Cross-functional leadership"
        ])
        self.assertIsNone(jobs[0]["match_label"])
        self.assertEqual(jobs[0]["review_state"], "new")

    def test_reimport_is_idempotent(self):
        importer = BenchmarkImporter(self.database)
        importer.import_payload(benchmark_payload())
        second = importer.import_payload(benchmark_payload())

        self.assertEqual(second["unchanged"], 1)
        with JobStore(self.database) as store:
            self.assertEqual(
                store.connection.execute("SELECT COUNT(*) FROM jobs").fetchone()[0], 1
            )
            self.assertEqual(
                store.connection.execute(
                    "SELECT COUNT(*) FROM benchmark_candidates"
                ).fetchone()[0],
                1,
            )

    def test_scheduled_result_merges_with_existing_direct_posting(self):
        payload = benchmark_payload()
        with JobStore(self.database) as store:
            store.upsert_jobs([{
                "external_id": "direct-42",
                "source": "greenhouse",
                "company": "Builder Company",
                "title": "Director of Technical Marketing",
                "location": "Remote - US",
                "description": "Complete employer posting.",
                "canonical_url": payload["jobs"][0]["canonical_url"],
            }])

        BenchmarkImporter(self.database).import_payload(payload)
        with JobStore(self.database) as store:
            jobs = store.list_active_jobs()
            self.assertEqual(len(jobs), 1)
            self.assertEqual(jobs[0]["source"], "greenhouse")
            self.assertEqual(jobs[0]["description"], "Complete employer posting.")
            self.assertEqual(
                store.connection.execute(
                    "SELECT COUNT(*) FROM job_discoveries"
                ).fetchone()[0],
                2,
            )

    def test_missing_selection_rationale_is_rejected(self):
        payload = benchmark_payload()
        del payload["jobs"][0]["selection_rationale"]

        with self.assertRaises(BenchmarkImportError):
            BenchmarkImporter(self.database).import_payload(payload)

    def test_report_measures_only_user_confirmed_discovery_recall(self):
        payload = benchmark_payload()
        BenchmarkImporter(self.database).import_payload(payload)
        service = ReviewQueueService(self.database, PROFILE_PATH)
        job = service.list_jobs()[0]

        pending = build_benchmark_report(self.database)
        self.assertEqual(pending["pending_review"], 1)
        self.assertIsNone(pending["confirmed_discovery_recall"])

        service.save_review(
            job["database_id"], "saved", "strong_match", ["responsibilities_fit"], ""
        )
        missed = build_benchmark_report(self.database)
        self.assertEqual(missed["confirmed_positive"], 1)
        self.assertEqual(missed["confirmed_discovery_recall"], 0.0)
        self.assertEqual(len(missed["missed_confirmed_jobs"]), 1)

        with JobStore(self.database) as store:
            store.upsert_jobs([{
                "external_id": "direct-99",
                "source": "greenhouse",
                "company": "Builder Company",
                "title": "Director of Technical Marketing",
                "location": "Remote - US",
                "description": "Complete employer posting.",
                "canonical_url": payload["jobs"][0]["canonical_url"],
            }])
        found = build_benchmark_report(self.database)
        self.assertEqual(found["confirmed_discovery_recall"], 1.0)
        self.assertEqual(found["candidates"][0]["independent_sources"], ["greenhouse"])


if __name__ == "__main__":
    unittest.main()
