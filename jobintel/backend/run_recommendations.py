from backend.jobs.job_aggregator import JobAggregator
from backend.jobs.job_embedding_service import JobEmbeddingService
from backend.ai.embedding_service import generate_embedding
from backend.ai.skill_extractor import SkillExtractor
from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.ai.ranking_engine import RankingEngine


def load_profile():
    from backend.profile.loader import load_profile
    return load_profile()


def run():
    print("\n=== JOBINTEL PIPELINE START ===")

    # profile
    profile_text = load_profile()

    skill_extractor = SkillExtractor()

    profile_vector = generate_embedding(profile_text)
    profile_skills = skill_extractor.extract(profile_text)

    print(f"[1] Profile loaded | skills: {len(profile_skills)}")

    # jobs
    aggregator = JobAggregator()
    raw_jobs = aggregator.fetch_all_jobs()

    print(f"[2] Jobs fetched: {len(raw_jobs)}")

    ingestion = JobIngestionPipeline()
    jobs = ingestion.load_from_list(raw_jobs)

    embedder = JobEmbeddingService()
    embedded_jobs = embedder.embed_jobs(jobs)

    print("[3] Jobs embedded")

    engine = RankingEngine(profile_vector, profile_skills)
    ranked = engine.rank_jobs(embedded_jobs)

    print("[4] Ranking complete")

    print("\n=== TOP JOB MATCHES ===\n")

    for i, job in enumerate(ranked[:10], 1):
        print(
            f"{i}. {job['title']} @ {job['company']} "
            f"Score: {job['score']:.4f} "
            f"Skills: {job['skills']}"
        )

    print("\n=== PIPELINE COMPLETE ===")


if __name__ == "__main__":
    run()