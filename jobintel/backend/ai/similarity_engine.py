from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import logging


logger = logging.getLogger(__name__)


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> List[float]:
    """
    Convert text into vector embedding.
    """

    if not text or not text.strip():
        raise ValueError("Input text cannot be empty.")

    logger.info("Generating embedding...")

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    return embedding.tolist()


def calculate_similarity(text_a: str, text_b: str) -> float:
    """
    Calculate cosine similarity between two texts.
    """

    embedding_a = generate_embedding(text_a)
    embedding_b = generate_embedding(text_b)

    similarity = cosine_similarity(
        [embedding_a],
        [embedding_b]
    )[0][0]

    logger.info(f"Similarity score: {similarity:.4f}")

    return float(similarity)