from sentence_transformers import SentenceTransformer

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