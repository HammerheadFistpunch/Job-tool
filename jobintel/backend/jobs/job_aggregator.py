from pathlib import Path

from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher
from backend.jobs.fetchers.lever_fetcher import LeverFetcher
from backend.jobs.fetchers.jobicy_fetcher import JobicyFetcher
from backend.jobs.prefilter import MarketPrefilter
from backend.jobs.source_config import DEFAULT_SOURCE_CONFIG, load_source_config


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
            configuration = load_source_config(config_path or DEFAULT_SOURCE_CONFIG)
            self.filter = MarketPrefilter(configuration.get("filters"))
            self.sources = self._load_sources(configuration) + self._load_discovery_sources(configuration)
        if not hasattr(self, "filter"):
            self.filter = MarketPrefilter({"enabled": False})

    def _load_sources(self, configuration):
        sources = []
        for item in configuration.get("sources", []):
            if not item.get("enabled", True):
                continue
            source_type = str(item.get("type", "")).lower()
            company = str(item.get("company", "")).strip()
            if source_type not in FETCHERS:
                raise ValueError(f"Unsupported job source type: {source_type}")
            if not company:
                raise ValueError("Every enabled job source requires a company token")
            fetcher = FETCHERS[source_type](company)
            fetcher.display_name = str(item.get("display_name") or company)
            sources.append(fetcher)
        return sources

    def _load_discovery_sources(self, configuration):
        sources = []
        for provider in configuration.get("discovery_sources", []):
            if not provider.get("enabled", True):
                continue
            source_type = str(provider.get("type", "")).lower()
            if source_type != "jobicy":
                raise ValueError(f"Unsupported discovery source type: {source_type}")
            defaults = {
                key: value for key, value in provider.items()
                if key not in {"queries", "enabled", "type"}
            }
            for query in provider.get("queries", []):
                if query.get("enabled", True):
                    sources.append(JobicyFetcher(dict(defaults, **query)))
        return sources

    def fetch_all_jobs(self):
        jobs, _errors, _reports = self.fetch_all_jobs_with_report()
        return jobs

    def fetch_all_jobs_with_report(self):
        all_jobs = []
        errors = []
        reports = []

        for source in self.sources:
            try:
                jobs = source.fetch()
                if getattr(source, "is_employer_source", True):
                    for job in jobs or []:
                        job["company"] = getattr(source, "display_name", source.company)
                accepted, filtered = self.filter.filter(jobs or [])
                all_jobs.extend(accepted)
                source_name = getattr(
                    source, "source_name",
                    source.__class__.__name__.replace("Fetcher", "").lower(),
                )
                reports.append({
                    "source": source_name,
                    "company": getattr(source, "display_name", getattr(source, "company", "")),
                    "token": getattr(source, "company", ""),
                    "scope": getattr(source, "scope", getattr(source, "display_name", source.company)),
                    "query_name": getattr(source, "query_name", ""),
                    "query_params": getattr(source, "params", {}),
                    "location_scope": getattr(source, "location_scope", ""),
                    "provider_count": getattr(source, "provider_count", len(jobs or [])),
                    "rate_limit": getattr(source, "rate_limit", {}),
                    "status": "success",
                    "fetched": len(jobs or []),
                    "accepted": len(accepted),
                    "filtered": filtered,
                    "external_ids": [str(job.get("external_id") or job.get("id") or "") for job in accepted],
                })
            except Exception as error:
                failure = {
                    "source": getattr(
                        source, "source_name",
                        source.__class__.__name__.replace("Fetcher", "").lower(),
                    ),
                    "company": getattr(source, "display_name", getattr(source, "company", "")),
                    "token": getattr(source, "company", ""),
                    "scope": getattr(source, "scope", getattr(source, "display_name", source.company)),
                    "query_name": getattr(source, "query_name", ""),
                    "query_params": getattr(source, "params", {}),
                    "location_scope": getattr(source, "location_scope", ""),
                    "provider_count": getattr(source, "provider_count", 0),
                    "rate_limit": getattr(source, "rate_limit", {}),
                    "error": str(error),
                }
                errors.append(failure)
                reports.append(dict(failure, status="failed", fetched=0, accepted=0, filtered=0))

        return all_jobs, errors, reports
