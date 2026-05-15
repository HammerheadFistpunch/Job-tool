import numpy as np
from typing import List, Dict


def cosine(a, b):
    a = np.array(a)
    b = np.array(b)

    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0

    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def skill_overlap(profile_skills, job_skills):
    if not profile_skills or not job_skills:
        return 0.0

    p = set(profile_skills)
    j = set(job_skills)

    return len(p & j) / len(p | j)


class RankingEngine:
    """
    Smarter ranking:
    - semantic similarity
    - normalized skill overlap
    - skill density boost
    """

    def __init__(self, profile_vector: List[float], profile_skills: List[str]):
        self.profile_vector = profile_vector
        self.profile_skills = profile_skills

    def score_job(self, job: Dict) -> float:

        semantic = cosine(self.profile_vector, job["vector"])
        skills = skill_overlap(self.profile_skills, job.get("skills", []))

        # skill density (reward richer matches)
        density = len(job.get("skills", [])) / 10.0
        density = min(density, 1.0)

        return (
            0.65 * semantic +
            0.30 * skills +
            0.05 * density
        )

    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        scored = []

        for job in jobs:
            score = self.score_job(job)

            scored.append({
                "job_id": job.get("job_id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "score": score,
                "skills": job.get("skills", [])
            })

        return sorted(scored, key=lambda x: x["score"], reverse=True)