from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str):
    """
    Convert text into vector embedding.
    """

    return model.encode(text)


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

    return float(similarity)
