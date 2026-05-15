def build_profile_text(profile: dict) -> str:
    sections = []

    metadata = profile["metadata"]

    sections.extend(metadata.get("target_roles", []))
    sections.extend(metadata.get("semantic_roles", []))
    sections.extend(metadata.get("industries", []))

    sections.append(profile["content"])

    return "\n".join(sections)
