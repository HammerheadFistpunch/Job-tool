from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher


class JobAggregator:
    """
    Central entry point for collecting jobs from multiple sources.
    """

    def __init__(self):
        self.sources = [
            GreenhouseFetcher("airbnb"),
            GreenhouseFetcher("stripe"),
            GreenhouseFetcher("dropbox"),
        ]

    def fetch_all_jobs(self):
        all_jobs = []

        for source in self.sources:
            try:
                jobs = source.fetch()

                if jobs:
                    all_jobs.extend(jobs)

            except Exception:
                print(f"[WARN] {source.__class__.__name__} skipped")

        return all_jobs