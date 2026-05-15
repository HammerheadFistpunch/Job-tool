import numpy as np
from typing import List, Dict


def cosine_similarity(vec1, vec2) -> float:
    """
    Compute cosine similarity between two vectors.
    """

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0

    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


class RankingEngine:
    """
    Ranks jobs based on similarity to a profile embedding.
    """

    def __init__(self, profile_vector: List[float]):
        self.profile_vector = profile_vector

    def rank_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Takes a list of embedded jobs and returns ranked results.
        Each job must contain:
            - job_id
            - vector
        """

        scored_jobs = []

        for job in jobs:
            score = cosine_similarity(self.profile_vector, job["vector"])

            scored_jobs.append({
                "job_id": job.get("job_id"),
                "score": score,
                "raw_text": job.get("raw_text", "")
            })

        # sort descending by similarity score
        ranked = sorted(scored_jobs, key=lambda x: x["score"], reverse=True)

        return ranked
