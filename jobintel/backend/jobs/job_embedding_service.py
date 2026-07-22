from backend.ai.embedding_service import generate_embedding, generate_embeddings
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
        fields = self.normalizer.normalize_fields(job)
        vector = generate_embedding(text)
        field_vector_list = generate_embeddings(list(fields.values()))
        field_vectors = dict(zip(fields.keys(), field_vector_list))

        skills = self.skill_extractor.extract(text)

        return {
            "job_id": job.get("id"),
            "vector": vector,
            "field_vectors": field_vectors,
            "raw_text": text,
            "skills": skills,
            "company": job.get("company"),
            "title": job.get("title"),
            "location": job.get("location"),
            "canonical_url": job.get("canonical_url") or job.get("source_url"),
        }

    def embed_jobs(self, jobs: list):
        if not jobs:
            return []

        normalized = []
        embedding_inputs = []

        for job in jobs:
            text = self.normalizer.normalize(job)
            fields = self.normalizer.normalize_fields(job)
            normalized.append((job, text, fields))
            embedding_inputs.extend([text, *fields.values()])

        vectors = generate_embeddings(embedding_inputs)
        embedded_jobs = []

        for index, (job, text, fields) in enumerate(normalized):
            offset = index * 4
            combined_vector = vectors[offset]
            field_vector_list = vectors[offset + 1:offset + 4]

            embedded_jobs.append({
                "job_id": job.get("id"),
                "vector": combined_vector,
                "field_vectors": dict(zip(fields.keys(), field_vector_list)),
                "raw_text": text,
                "skills": self.skill_extractor.extract(text),
                "company": job.get("company"),
                "title": job.get("title"),
                "location": job.get("location"),
                "canonical_url": job.get("canonical_url") or job.get("source_url"),
            })

        return embedded_jobs
