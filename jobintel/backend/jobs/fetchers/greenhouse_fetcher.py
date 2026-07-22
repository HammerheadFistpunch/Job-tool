import logging
import time
from typing import Callable, Dict, List

try:
    import requests
except ImportError:  # Allows dependency-light storage/unit tests to run.
    requests = None


LOGGER = logging.getLogger(__name__)


class JobFetchError(RuntimeError):
    pass


class GreenhouseFetcher:
    def __init__(
        self,
        company: str,
        http_get: Callable | None = None,
        retries: int = 3,
    ):
        self.company = company
        self.url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        if http_get is None and requests is None:
            raise RuntimeError(
                "The requests package is required for live Greenhouse collection"
            )
        self.http_get = http_get or requests.get
        self.retries = retries

    def fetch(self) -> List[Dict]:
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.http_get(
                    self.url,
                    params={"content": "true"},
                    timeout=20,
                )
                response.raise_for_status()
                data = response.json()
                return [self._normalize(job) for job in data.get("jobs", [])]
            except Exception as error:
                last_error = error
                LOGGER.warning(
                    "Greenhouse fetch failed for %s (attempt %s/%s): %s",
                    self.company, attempt, self.retries, error,
                )
                if attempt < self.retries:
                    time.sleep(min(2 ** (attempt - 1), 4))

        raise JobFetchError(
            f"Greenhouse fetch failed for {self.company}: {last_error}"
        ) from last_error

    def _normalize(self, job: Dict) -> Dict:
        return {
            "id": str(job.get("id", "")),
            "external_id": str(job.get("id", "")),
            "title": job.get("title", ""),
            "company": self.company,
            "location": (job.get("location") or {}).get("name", ""),
            "description": job.get("content", ""),
            "source": "greenhouse",
            "canonical_url": job.get("absolute_url", ""),
            "source_url": job.get("absolute_url", ""),
            "posted_at": job.get("created_at", ""),
            "updated_at": job.get("updated_at", ""),
            "raw": job,
        }
