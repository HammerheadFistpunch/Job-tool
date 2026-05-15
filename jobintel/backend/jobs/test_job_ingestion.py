from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.jobs.job_embedding_service import JobEmbeddingService


def run_test():
    pipeline = JobIngestionPipeline()

    # sample inline dataset
    jobs = [
        {
            "id": "1",
            "title": "Software Engineer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "Python, backend systems, APIs"
        },
        {
            "id": "2",
            "title": "Marketing Manager",
            "company": "BrandCo",
            "location": "NYC",
            "description": "SEO, campaigns, social media"
        }
    ]

    jobs = pipeline.load_from_list(jobs)

    embedder = JobEmbeddingService()
    embedded = embedder.embed_jobs(jobs)

    print("\n=== INGESTION TEST ===")
    for job in embedded:
        print(job["job_id"], len(job["vector"]))


if __name__ == "__main__":
    run_test()
