import json
from pathlib import Path

from backend.profile.schema import CandidateProfile


PROFILE_PATH = Path("data/input/Profiles/pr_profile.md")
STRUCTURED_PROFILE_PATH = Path("data/input/Profiles/patrick_profile.json")


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


def load_structured_profile(path: str | Path | None = None) -> CandidateProfile:
    """Load and validate the deterministic matching profile."""

    profile_path = Path(path) if path else STRUCTURED_PROFILE_PATH
    if not profile_path.exists():
        raise FileNotFoundError(f"Structured profile not found: {profile_path}")
    try:
        data = json.loads(profile_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Structured profile contains invalid JSON: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("Structured profile must contain one JSON object")
    return CandidateProfile.from_dict(data)
