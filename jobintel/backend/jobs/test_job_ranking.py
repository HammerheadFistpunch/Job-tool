from backend.profile.loader import load_profile  # adjust if your function name differs
from backend.ai.embedding_service import generate_embedding
from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.jobs.job_embedding_service import JobEmbeddingService
from backend.ai.ranking_engine import RankingEngine


def run_test():
    # 1. Load profile
    profile_text = load_profile()
    profile_vector = generate_embedding(profile_text)

    # 2. Sample jobs
    jobs = [
        {
            "id": "1",
            "title": "Backend Engineer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "Python APIs, microservices, distributed systems"
        },
        {
            "id": "2",
            "title": "Graphic Designer",
            "company": "DesignCo",
            "location": "NYC",
            "description": "Photoshop, branding, illustration"
        },
        {
            "id": "3",
            "title": "Software Engineer",
            "company": "StartupX",
            "location": "Remote",
            "description": "Python, backend systems, cloud infrastructure"
        }
    ]

    # 3. Ingest + embed jobs
    ingestion = JobIngestionPipeline()
    jobs = ingestion.load_from_list(jobs)

    embedder = JobEmbeddingService()
    embedded_jobs = embedder.embed_jobs(jobs)

    # 4. Rank
    engine = RankingEngine(profile_vector)
    ranked = engine.rank_jobs(embedded_jobs)

    # 5. Output
    print("\n=== RANKED JOBS ===")
    for i, job in enumerate(ranked, 1):
        print(f"{i}. Job {job['job_id']} — Score: {job['score']:.4f}")


if __name__ == "__main__":
    run_test()
