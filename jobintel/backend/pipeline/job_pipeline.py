from backend.jobs.models import Job


def process_job(job_data: dict):
    """
    Initial pipeline placeholder.
    """

    print("Processing job...")
    print(job_data)

    return Job(
        company=job_data["company"],
        title=job_data["title"],
        location=job_data["location"],
        description=job_data["description"],
        source_url=job_data["source_url"],
        smi_score=0.0,
    )
