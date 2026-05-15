from pathlib import Path


PROFILE_PATH = Path("data/input/Profiles/pr_profile.md")


def load_profile() -> str:
    """
    Loads the canonical markdown candidate profile.

    Returns:
        str: Full markdown profile text.
    """

    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"Profile file not found: {PROFILE_PATH}"
        )

    profile_text = PROFILE_PATH.read_text(
        encoding="utf-8"
    ).strip()

    if not profile_text:
        raise ValueError(
            "Profile file is empty."
        )

    return profile_text