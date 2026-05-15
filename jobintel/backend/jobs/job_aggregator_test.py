from backend.jobs.job_aggregator import JobAggregator


def run():
    aggregator = JobAggregator()

    jobs = aggregator.fetch_all_jobs()

    print("\n=== TOTAL JOBS ===")
    print(len(jobs))

    print("\nSample:")
    for job in jobs[:5]:
        print(job["title"], "-", job["company"])


if __name__ == "__main__":
    run()
