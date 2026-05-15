from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher


class JobAggregator:
    """
    Central entry point for collecting jobs from all sources.
    """

    def __init__(self):
        self.sources = [
            GreenhouseFetcher("airbnb"),
            GreenhouseFetcher("stripe"),
            GreenhouseFetcher("shopify"),
        ]

    def fetch_all_jobs(self):
        all_jobs = []

        for source in self.sources:
            try:
                jobs = source.fetch()
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Source error: {source}: {e}")

        return all_jobs
