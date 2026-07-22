import logging
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List

try:
    import requests
except ImportError:  # Allows dependency-light storage/unit tests to run.
    requests = None

from backend.jobs.fetchers.greenhouse_fetcher import JobFetchError


LOGGER = logging.getLogger(__name__)


class LeverFetcher:
    def __init__(
        self,
        company: str,
        http_get: Callable | None = None,
        retries: int = 3,
    ):
        self.company = company
        self.url = f"https://api.lever.co/v0/postings/{company}"
        if http_get is None and requests is None:
            raise RuntimeError("The requests package is required for live Lever collection")
        self.http_get = http_get or requests.get
        self.retries = retries

    def fetch(self) -> List[Dict]:
        last_error = None
        for attempt in range(1, self.retries + 1):
            try:
                response = self.http_get(
                    self.url,
                    params={"mode": "json"},
                    timeout=20,
                )
                response.raise_for_status()
                return [self._normalize(job) for job in response.json()]
            except Exception as error:
                last_error = error
                LOGGER.warning(
                    "Lever fetch failed for %s (attempt %s/%s): %s",
                    self.company, attempt, self.retries, error,
                )
                if attempt < self.retries:
                    time.sleep(min(2 ** (attempt - 1), 4))

        raise JobFetchError(f"Lever fetch failed for {self.company}: {last_error}") from last_error

    def _normalize(self, job: Dict) -> Dict:
        categories = job.get("categories") or {}
        created_at = job.get("createdAt")
        if isinstance(created_at, (int, float)):
            created_at = datetime.fromtimestamp(
                created_at / 1000, tz=timezone.utc
            ).isoformat()

        sections = [job.get("descriptionPlain") or job.get("description") or ""]
        for section in job.get("lists") or []:
            label = section.get("text") or ""
            content = section.get("content") or ""
            sections.append(f"{label}\n{content}".strip())
        sections.append(job.get("additionalPlain") or job.get("additional") or "")
        description = "\n\n".join(section for section in sections if section).strip()

        return {
            "id": str(job.get("id", "")),
            "external_id": str(job.get("id", "")),
            "title": job.get("text", ""),
            "company": self.company,
            "location": categories.get("location", ""),
            "description": description,
            "source": "lever",
            "canonical_url": job.get("hostedUrl") or job.get("applyUrl") or "",
            "source_url": job.get("hostedUrl") or job.get("applyUrl") or "",
            "posted_at": created_at or "",
            "updated_at": "",
            "raw": job,
        }
