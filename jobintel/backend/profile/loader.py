# backend/profile/loader.py

from pathlib import Path
import frontmatter


PROFILE_PATH = Path("data/profiles/patrick_rich_profile.md")


def load_profile():
    profile = frontmatter.load(PROFILE_PATH)

    return {
        "metadata": profile.metadata,
        "content": profile.content,
        "raw": str(profile)
    }
