import json
import tempfile
import unittest
from pathlib import Path

from backend.jobs.prefilter import MarketPrefilter
from backend.jobs.source_config import load_source_config, set_source_enabled
from backend.storage.job_store import JobStore


class MarketPrefilterTests(unittest.TestCase):
    def setUp(self):
        self.filter = MarketPrefilter({
            "enabled": True,
            "title_terms": ["marketing", "communications", "content"],
            "excluded_title_terms": ["sales development representative"],
            "location_terms": ["remote", "utah", "salt lake"],
        })

    def test_keeps_relevant_remote_and_local_jobs(self):
        self.assertTrue(self.filter.accepts({"title": "Product Marketing Manager", "location": "Remote - US"}))
        self.assertTrue(self.filter.accepts({"title": "Communications Director", "location": "Salt Lake City, Utah"}))

    def test_rejects_wrong_role_or_location(self):
        self.assertFalse(self.filter.accepts({"title": "Software Engineer", "location": "Remote"}))
        self.assertFalse(self.filter.accepts({"title": "Content Manager", "location": "New York, NY"}))


class SourceConfigurationTests(unittest.TestCase):
    def test_toggle_preserves_registry_and_filters(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sources.json"
            path.write_text(json.dumps({
                "filters": {"enabled": True},
                "sources": [{"type": "greenhouse", "company": "example", "enabled": True}],
            }), encoding="utf-8")
            set_source_enabled("greenhouse", "example", False, path)
            data = load_source_config(path)
            self.assertFalse(data["sources"][0]["enabled"])
            self.assertTrue(data["filters"]["enabled"])


class SourceExpirationTests(unittest.TestCase):
    def test_only_missing_jobs_on_successful_source_are_expired(self):
        with tempfile.TemporaryDirectory() as directory:
            with JobStore(Path(directory) / "test.db") as store:
                jobs = [
                    {"external_id": "keep", "source": "greenhouse", "company": "Example", "title": "Marketing Manager"},
                    {"external_id": "close", "source": "greenhouse", "company": "Example", "title": "Content Manager"},
                    {"external_id": "other", "source": "greenhouse", "company": "Other", "title": "Marketing Lead"},
                ]
                store.upsert_jobs(jobs)
                expired = store.expire_missing_from_source("greenhouse", "Example", ["keep"])
                self.assertEqual(expired, 1)
                active_ids = {job["id"] for job in store.list_active_jobs()}
                self.assertEqual(active_ids, {"keep", "other"})

    def test_empty_successful_board_expires_all_its_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            with JobStore(Path(directory) / "test.db") as store:
                store.upsert_jobs([{"external_id": "old", "source": "lever", "company": "Example", "title": "Content Lead"}])
                self.assertEqual(store.expire_missing_from_source("lever", "Example", []), 1)
                self.assertEqual(store.list_active_jobs(), [])


if __name__ == "__main__":
    unittest.main()
