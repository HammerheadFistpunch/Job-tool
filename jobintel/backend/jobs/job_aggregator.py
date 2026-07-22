import json
from pathlib import Path

from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher
from backend.jobs.fetchers.lever_fetcher import LeverFetcher


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONFIG = PROJECT_ROOT / "config" / "job_sources.json"
FETCHERS = {
    "greenhouse": GreenhouseFetcher,
    "lever": LeverFetcher,
}


class JobAggregator:
    """Collect jobs from enabled ATS sources listed in a JSON config file."""

    def __init__(self, sources=None, config_path: str | Path | None = None):
        if sources is not None:
            self.sources = sources
        else:
            self.sources = self._load_sources(config_path or DEFAULT_SOURCE_CONFIG)

    def _load_sources(self, config_path: str | Path):
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Job source configuration not found: {path}")

        with path.open("r", encoding="utf-8") as handle:
            configured = json.load(handle).get("sources", [])

        sources = []
        for item in configured:
            if not item.get("enabled", True):
                continue
            source_type = str(item.get("type", "")).lower()
            company = str(item.get("company", "")).strip()
            if source_type not in FETCHERS:
                raise ValueError(f"Unsupported job source type: {source_type}")
            if not company:
                raise ValueError("Every enabled job source requires a company token")
            sources.append(FETCHERS[source_type](company))
        return sources

    def fetch_all_jobs(self):
        jobs, _errors = self.fetch_all_jobs_with_report()
        return jobs

    def fetch_all_jobs_with_report(self):
        all_jobs = []
        errors = []

        for source in self.sources:
            try:
                jobs = source.fetch()
                if jobs:
                    all_jobs.extend(jobs)
            except Exception as error:
                errors.append({
                    "source": source.__class__.__name__,
                    "company": getattr(source, "company", ""),
                    "error": str(error),
                })

        return all_jobs, errors
