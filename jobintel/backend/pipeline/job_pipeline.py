from backend.ai.similarity_engine import calculate_similarity

from backend.jobs.models import Job
from backend.jobs.sample_jobs import SAMPLE_JOB

from backend.storage.database import SessionLocal


CAREER_REFERENCE = """
MBA focused on leadership and strategy.

Experienced in:
- marketing
- communications
- creative production
- journalism
- video production
- scripting
- media creation
- campaign strategy
"""


def process_job(job_data: dict):

    similarity_score = calculate_similarity(
        CAREER_REFERENCE,
        job_data["description"]
    )

    db = SessionLocal()

    job = Job(
        company=job_data["company"],
        title=job_data["title"],
        location=job_data["location"],
        description=job_data["description"],
        source_url=job_data["source_url"],
        smi_score=similarity_score,
    )

    db.add(job)
    db.commit()

    print("Job saved.")
    print(f"Similarity Score: {similarity_score:.4f}")

    db.close()


if __name__ == "__main__":
    process_job(SAMPLE_JOB)