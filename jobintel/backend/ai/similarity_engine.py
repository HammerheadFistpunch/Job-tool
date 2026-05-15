import numpy as np


def cosine_similarity(
    embedding_a: list[float],
    embedding_b: list[float]
) -> float:
    """
    Compute cosine similarity between two vectors.
    """

    a = np.array(embedding_a)
    b = np.array(embedding_b)

    similarity = np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )

    return float(similarity)