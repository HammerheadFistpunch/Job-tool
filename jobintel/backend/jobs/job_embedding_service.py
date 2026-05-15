from backend.ai.embedding_service import generate_embedding
from backend.jobs.job_normalizer import JobNormalizer
from backend.ai.skill_extractor import SkillExtractor


class JobEmbeddingService:
    """
    Converts jobs into embeddings + structured skill metadata.
    """

    def __init__(self):
        self.normalizer = JobNormalizer()
        self.skill_extractor = SkillExtractor()

    def embed_job(self, job: dict):
        text = self.normalizer.normalize(job)

        vector = generate_embedding(text)

        skills = self.skill_extractor.extract(text)

        return {
            "job_id": job.get("id"),
            "vector": vector,
            "raw_text": text,
            "skills": skills,
            "company": job.get("company"),
            "title": job.get("title")
        }

    def embed_jobs(self, jobs: list):
        return [self.embed_job(job) for job in jobs]