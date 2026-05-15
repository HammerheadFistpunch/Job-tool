from backend.jobs.fetchers.greenhouse_fetcher import GreenhouseFetcher


def run():
    fetcher = GreenhouseFetcher("airbnb")

    jobs = fetcher.fetch()

    print("\n=== GREENHOUSE JOBS ===")
    for job in jobs[:5]:
        print(job["title"], "-", job["location"])


if __name__ == "__main__":
    run()
