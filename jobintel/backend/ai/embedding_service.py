from sentence_transformers import SentenceTransformer
from typing import Sequence

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate semantic embedding vector from text using SentenceTransformer.
    """

    if not text or not text.strip():
        raise ValueError("Input text is empty.")

    vector = model.encode(text)
    return vector.tolist()


def generate_embeddings(texts: Sequence[str]) -> list[list[float]]:
    """Generate embeddings for a batch of non-empty text values."""

    if not texts:
        return []

    if any(not text or not text.strip() for text in texts):
        raise ValueError("Embedding inputs must not be empty.")

    vectors = model.encode(list(texts))
    return vectors.tolist()
