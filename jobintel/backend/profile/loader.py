from pathlib import Path

from backend.profile.schema import CandidateProfile


PROFILE_PATH = Path("data/input/Profiles/pr_profile.md")


SECTION_MAP = {
    "Goals": "goals",
    "Strengths": "strengths",
    "Preferred Roles": "preferred_roles",
    "Exclusions": "exclusions",
    "Work Preferences": "work_preferences",
}


def load_profile() -> CandidateProfile:
    """
    Load and parse markdown profile into structured CandidateProfile.
    """

    parsed = {
        "goals": [],
        "strengths": [],
        "preferred_roles": [],
        "exclusions": [],
        "work_preferences": [],
    }

    current_section = None

    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Detect section headers
            if line.startswith("# "):
                section_name = line.replace("# ", "").strip()
                current_section = SECTION_MAP.get(section_name)
                continue

            # Parse list items
            if line.startswith("- ") and current_section:
                parsed[current_section].append(line[2:].strip())

    return CandidateProfile(**parsed)