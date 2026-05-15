from backend.profile.loader import load_profile
from backend.ai.embedding_service import generate_embedding


def main():
    profile = load_profile()

    embedding = generate_embedding(profile)

    print("\n=== EMBEDDING SUCCESS ===\n")

    print(f"Vector Length: {len(embedding)}")

    print("\nFirst 10 Values:\n")

    print(embedding[:10])


if __name__ == "__main__":
    main()
