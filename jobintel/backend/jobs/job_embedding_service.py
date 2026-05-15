from backend.ai.embedding_service import generate_embedding
from backend.jobs.job_normalizer import JobNormalizer


class JobEmbeddingService:
    """
    Converts structured job objects into embedding vectors.
    """

    def __init__(self):
        self.normalizer = JobNormalizer()

    def embed_job(self, job: dict) -> dict:
        """
        Convert a single job into an embedding representation.
        """

        text = self.normalizer.normalize(job)
        vector = generate_embedding(text)

        return {
            "job_id": job.get("id", ""),
            "vector": vector,
            "raw_text": text
        }

    def embed_jobs(self, jobs: list[dict]) -> list[dict]:
        """
        Batch convert jobs into embeddings.
        """

        return [self.embed_job(job) for job in jobs]