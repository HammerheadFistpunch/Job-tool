from backend.profile.loader import load_profile
from backend.ai.embedding_service import generate_embedding
from backend.ai.similarity_engine import cosine_similarity


GOOD_JOB = """
Director of Technical Marketing

Seeking a technical marketing leader capable of
translating engineering concepts into strategic
market positioning and cross-functional messaging.

Must work closely with engineering, product,
and executive leadership teams.

Experience with AI systems, technical storytelling,
and complex systems communication preferred.
"""

BAD_JOB = """
Entry-Level Insurance Sales Representative

Seeking aggressive outbound cold-calling professionals
for high-volume commission-only sales environment.

No technical experience required.
"""


def main():
    profile = load_profile()

    profile_embedding = generate_embedding(profile)

    good_embedding = generate_embedding(GOOD_JOB)

    bad_embedding = generate_embedding(BAD_JOB)

    good_score = cosine_similarity(
        profile_embedding,
        good_embedding
    )

    bad_score = cosine_similarity(
        profile_embedding,
        bad_embedding
    )

    print("\n=== SIMILARITY RESULTS ===\n")

    print(f"GOOD JOB SCORE: {good_score:.4f}")

    print(f"BAD JOB SCORE:  {bad_score:.4f}")


if __name__ == "__main__":
    main()
