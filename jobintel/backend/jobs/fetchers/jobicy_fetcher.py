"""Query-driven collection from Jobicy's public remote-jobs API."""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict, List

try:
    import requests
except ImportError:  # Allows dependency-light storage/unit tests to run.
    requests = None

from backend.jobs.fetchers.greenhouse_fetcher import JobFetchError


LOGGER = logging.getLogger(__name__)


class JobicyFetcher:
    """Fetch one configured market query without requiring an API key."""

    source_name = "jobicy"
    is_employer_source = False
    url = "https://jobicy.com/api/v2/remote-jobs"

    def __init__(
        self,
        query: Dict,
        http_get: Callable | None = None,
        retries: int = 3,
    ):
        self.query = dict(query)
        self.query_name = str(query.get("name") or "jobicy-query").strip()
        self.company = self.query_name  # Compatibility with aggregator reports.
        self.display_name = str(query.get("display_name") or self.query_name)
        self.scope = self.query_name
        self.location_scope = str(query.get("location_scope") or "remote_us")
        self.params = {
            "count": min(max(int(query.get("count", 100)), 1), 100),
            "geo": str(query.get("geo") or "usa"),
            "tag": str(query.get("tag") or "").strip(),
        }
        self.params = {key: value for key, value in self.params.items() if value != ""}
        self.required_location_terms = [
            str(term).lower() for term in query.get("required_location_terms", [])
        ]
        if http_get is None and requests is None:
            raise RuntimeError("The requests package is required for live Jobicy collection")
        self.http_get = http_get or requests.get
        self.retries = retries
        self.provider_count = 0
        self.rate_limit: Dict[str, str] = {}

    def fetch(self) -> List[Dict]:
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.http_get(self.url, params=self.params, timeout=30)
                response.raise_for_status()
                payload = response.json()
                raw_jobs = payload.get("jobs") or []
                self.provider_count = int(payload.get("jobCount") or len(raw_jobs))
                headers = getattr(response, "headers", {}) or {}
                self.rate_limit = {
                    key: str(value)
                    for key, value in headers.items()
                    if "rate" in key.lower() or "retry-after" in key.lower()
                }
                jobs = [self._normalize(job) for job in raw_jobs]
                if self.required_location_terms:
                    jobs = [
                        job for job in jobs
                        if any(term in job["location"].lower() for term in self.required_location_terms)
                    ]
                return jobs
            except Exception as error:
                last_error = error
                LOGGER.warning(
                    "Jobicy query failed for %s (attempt %s/%s): %s",
                    self.query_name, attempt, self.retries, error,
                )
                if attempt < self.retries:
                    time.sleep(min(2 ** (attempt - 1), 4))

        raise JobFetchError(
            f"Jobicy query failed for {self.query_name}: {last_error}"
        ) from last_error

    def _normalize(self, job: Dict) -> Dict:
        url = str(job.get("url") or "")
        geography = str(job.get("jobGeo") or "").strip()
        location = f"Remote - {geography}" if geography else "Remote"
        return {
            "id": str(job.get("id") or ""),
            "external_id": str(job.get("id") or ""),
            "title": job.get("jobTitle") or "",
            "company": job.get("companyName") or "",
            "location": location,
            "description": job.get("jobDescription") or job.get("jobExcerpt") or "",
            "source": self.source_name,
            "canonical_url": url,
            "source_url": url,
            "posted_at": job.get("pubDate") or "",
            "updated_at": job.get("pubDate") or "",
            "discovery_scope": self.scope,
            "query_name": self.query_name,
            "location_scope": self.location_scope,
            "raw": job,
        }
