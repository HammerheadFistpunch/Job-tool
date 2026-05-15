def normalize_profile(profile):
    metadata = profile["metadata"]

    return {
        "target_roles": metadata.get("target_roles", []),
        "semantic_roles": metadata.get("semantic_roles", []),
        "industries": metadata.get("industries", []),
        "salary": metadata.get("salary", {}),
        "content": profile["content"]
    }
