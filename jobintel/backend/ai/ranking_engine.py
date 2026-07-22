import numpy as np
from typing import List, Dict


DEFAULT_FIELD_WEIGHTS = {
    "title": 0.50,
    "description": 0.40,
    "metadata": 0.10,
}


def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def skill_overlap(profile_skills, job_skills):
    if not profile_skills or not job_skills:
        return 0.0

    p = {skill.strip().lower() for skill in profile_skills if skill.strip()}
    j = {skill.strip().lower() for skill in job_skills if skill.strip()}

    return len(p & j) / len(p | j)


class RankingEngine:
    """
    Field-aware ranking that prioritizes title relevance, then description,
    then low-value metadata. Skill overlap is a separate supporting signal.
    """

    def __init__(
        self,
        profile_vector: List[float],
        profile_skills: List[str] | None = None,
        field_weights: Dict[str, float] | None = None,
    ):
        self.profile_vector = profile_vector
        self.profile_skills = profile_skills or []
        self.field_weights = field_weights or DEFAULT_FIELD_WEIGHTS.copy()
        self._validate_field_weights()

    def _validate_field_weights(self):
        expected_fields = set(DEFAULT_FIELD_WEIGHTS)

        if set(self.field_weights) != expected_fields:
            raise ValueError(
                f"Field weights must contain exactly: {sorted(expected_fields)}"
            )

        if any(weight < 0 for weight in self.field_weights.values()):
            raise ValueError("Field weights cannot be negative")

        if not np.isclose(sum(self.field_weights.values()), 1.0):
            raise ValueError("Field weights must sum to 1.0")

    def semantic_score(self, job: Dict) -> float:
        field_vectors = job.get("field_vectors")

        # Compatibility with jobs embedded before field-aware ranking existed.
        if not field_vectors:
            return cosine(self.profile_vector, job["vector"])

        missing = set(self.field_weights) - set(field_vectors)
        if missing:
            raise ValueError(f"Job is missing field vectors: {sorted(missing)}")

        return sum(
            self.field_weights[field]
            * cosine(self.profile_vector, field_vectors[field])
            for field in self.field_weights
        )

    def score_components(self, job: Dict) -> Dict[str, float]:
        semantic = self.semantic_score(job)
        skills = skill_overlap(self.profile_skills, job.get("skills", []))

        return {
            "semantic": semantic,
            "skills": skills,
            "total": 0.80 * semantic + 0.20 * skills,
        }

    def score_job(self, job: Dict) -> float:
        return self.score_components(job)["total"]

    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        scored = []

        for job in jobs:
            components = self.score_components(job)

            scored.append({
                "job_id": job.get("job_id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "canonical_url": job.get("canonical_url"),
                "score": components["total"],
                "score_components": components,
                "skills": job.get("skills", [])
            })

        return sorted(scored, key=lambda x: x["score"], reverse=True)
