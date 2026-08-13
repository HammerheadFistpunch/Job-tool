import tempfile
import unittest
from pathlib import Path

from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher, JobFetchError
from backend.jobs.fetchers.lever_fetcher import LeverFetcher
from backend.jobs.fetchers.jobicy_fetcher import JobicyFetcher
from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.storage.job_store import JobStore


class FakeResponse:
    def __init__(self, payload, status_code=200, headers=None):
        self.payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self.payload


class GreenhouseFetcherTests(unittest.TestCase):
    def test_requests_content_and_preserves_complete_record(self):
        calls = []

        def get(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse({"jobs": [{
                "id": 42,
                "title": "Marketing Manager",
                "location": {"name": "Remote"},
                "content": "<p>Lead content strategy</p>",
                "absolute_url": "https://example.test/jobs/42",
                "updated_at": "2026-07-22T12:00:00Z",
            }]})

        job = GreenhouseFetcher("example", http_get=get).fetch()[0]

        self.assertEqual(calls[0][1]["params"], {"content": "true"})
        self.assertEqual(job["description"], "<p>Lead content strategy</p>")
        self.assertEqual(job["canonical_url"], "https://example.test/jobs/42")
        self.assertEqual(job["external_id"], "42")

    def test_source_failure_is_visible(self):
        def get(_url, **_kwargs):
            return FakeResponse({}, status_code=503)

        fetcher = GreenhouseFetcher("example", http_get=get, retries=1)
        with self.assertRaises(JobFetchError):
            fetcher.fetch()


class LeverFetcherTests(unittest.TestCase):
    def test_preserves_description_url_location_and_date(self):
        calls = []

        def get(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse([{
                "id": "lever-7",
                "text": "Content Strategy Lead",
                "categories": {"location": "Remote - US"},
                "descriptionPlain": "Own editorial strategy.",
                "lists": [{
                    "text": "What you bring",
                    "content": "Seven years of communications experience.",
                }],
                "additionalPlain": "Manage agency partners.",
                "hostedUrl": "https://jobs.example.test/lever-7",
                "createdAt": 1784721600000,
            }])

        job = LeverFetcher("example", http_get=get).fetch()[0]

        self.assertEqual(calls[0][1]["params"], {"mode": "json"})
        self.assertIn("Manage agency partners", job["description"])
        self.assertIn("Seven years of communications", job["description"])
        self.assertEqual(job["location"], "Remote - US")
        self.assertEqual(job["canonical_url"], "https://jobs.example.test/lever-7")
        self.assertTrue(job["posted_at"].startswith("2026-"))


class JobicyFetcherTests(unittest.TestCase):
    def test_builds_query_and_normalizes_provider_record(self):
        calls = []

        def get(url, **kwargs):
            calls.append((url, kwargs))
            return FakeResponse({"jobCount": 1, "jobs": [{
                "id": 88,
                "url": "https://jobicy.com/jobs/88-example",
                "jobTitle": "Technical Marketing Director",
                "companyName": "Example",
                "jobGeo": "USA",
                "jobDescription": "Translate complex products.",
                "pubDate": "2026-08-13T10:00:00Z",
            }]}, headers={"X-RateLimit-Remaining": "99"})

        fetcher = JobicyFetcher({
            "name": "remote_technical_marketing",
            "tag": "technical marketing",
            "geo": "usa",
        }, http_get=get)
        job = fetcher.fetch()[0]

        self.assertEqual(calls[0][1]["params"]["tag"], "technical marketing")
        self.assertEqual(job["company"], "Example")
        self.assertEqual(job["source"], "jobicy")
        self.assertEqual(job["location"], "Remote - USA")
        self.assertEqual(job["discovery_scope"], "remote_technical_marketing")
        self.assertEqual(fetcher.provider_count, 1)
        self.assertEqual(fetcher.rate_limit["X-RateLimit-Remaining"], "99")

    def test_location_constrained_query_can_report_zero(self):
        def get(_url, **_kwargs):
            return FakeResponse({"jobCount": 1, "jobs": [{
                "id": 89, "jobTitle": "Marketing Director",
                "companyName": "Example", "jobGeo": "USA",
            }]})

        fetcher = JobicyFetcher({
            "name": "utah_marketing",
            "tag": "marketing",
            "required_location_terms": ["utah", "salt lake"],
        }, http_get=get)
        self.assertEqual(fetcher.fetch(), [])
        self.assertEqual(fetcher.provider_count, 1)


class JobStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store = JobStore(Path(self.temp_dir.name) / "test.db")
        self.job = JobIngestionPipeline().load_from_list([{
            "id": "42",
            "source": "greenhouse",
            "company": "Example",
            "title": "Marketing Manager",
            "location": "Remote",
            "description": "Lead content strategy",
            "canonical_url": "https://example.test/jobs/42",
            "updated_at": "2026-07-22T12:00:00Z",
        }])[0]

    def tearDown(self):
        self.store.close()
        self.temp_dir.cleanup()

    def test_repeated_collection_deduplicates_job(self):
        first = self.store.upsert_jobs([self.job])
        second = self.store.upsert_jobs([self.job])

        self.assertEqual(first.created, 1)
        self.assertEqual(second.unchanged, 1)
        self.assertEqual(len(self.store.list_active_jobs()), 1)

    def test_changed_job_updates_without_losing_identity(self):
        self.store.upsert_jobs([self.job])
        changed = dict(self.job, description="Lead global content strategy")
        result = self.store.upsert_jobs([changed])

        self.assertEqual(result.updated, 1)
        stored = self.store.list_active_jobs()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["description"], "Lead global content strategy")

    def test_cross_source_overlap_keeps_one_job_and_two_attributions(self):
        self.store.upsert_jobs([self.job])
        broad = dict(
            self.job,
            source="jobicy",
            external_id="jobicy-42",
            canonical_url="https://jobicy.com/jobs/42-example",
            source_url="https://jobicy.com/jobs/42-example",
            discovery_scope="remote_product_marketing",
        )
        result = self.store.upsert_jobs([broad])

        self.assertEqual(result.unchanged, 1)
        self.assertEqual(len(self.store.list_active_jobs()), 1)
        discoveries = self.store.connection.execute(
            "SELECT source, scope FROM job_discoveries ORDER BY source"
        ).fetchall()
        self.assertEqual(
            [(row["source"], row["scope"]) for row in discoveries],
            [("greenhouse", "example"), ("jobicy", "remote_product_marketing")],
        )

    def test_same_source_distinct_ids_are_not_merged_by_title(self):
        other = dict(
            self.job,
            external_id="43",
            canonical_url="https://example.test/jobs/search?gh_jid=43&utm_source=test",
            description="A separate opening with the same title.",
        )
        self.job["canonical_url"] = "https://example.test/jobs/search?gh_jid=42&utm_source=test"
        self.store.upsert_jobs([self.job, other])
        self.assertEqual(len(self.store.list_active_jobs()), 2)

    def test_collection_run_records_counts_and_errors(self):
        run_id = self.store.start_collection_run()
        summary = self.store.upsert_jobs([self.job])
        self.store.finish_collection_run(
            run_id, summary, [{"source": "greenhouse", "error": "timeout"}]
        )

        row = self.store.connection.execute(
            "SELECT * FROM collection_runs WHERE id = ?", (run_id,)
        ).fetchone()
        self.assertEqual(row["status"], "completed_with_errors")
        self.assertEqual(row["new_count"], 1)
        self.assertEqual(row["error_count"], 1)


if __name__ == "__main__":
    unittest.main()
