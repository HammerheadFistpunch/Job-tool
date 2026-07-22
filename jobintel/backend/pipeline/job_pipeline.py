"""Compatibility entry point for persisting a manually supplied job."""

from backend.storage.job_store import JobStore


def process_job(job_data: dict) -> None:
    with JobStore() as store:
        summary = store.upsert_jobs([job_data])

    action = "saved" if summary.created else "updated" if summary.updated else "already current"
    print(f"Job {action}.")


if __name__ == "__main__":
    from backend.jobs.sample_jobs import SAMPLE_JOB

    process_job(SAMPLE_JOB)
