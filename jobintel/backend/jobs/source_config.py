"""Read and safely update the local ATS source registry."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_CONFIG = PROJECT_ROOT / "config" / "job_sources.json"
SUPPORTED_TYPES = {"greenhouse", "lever"}


def load_source_config(path: str | Path = DEFAULT_SOURCE_CONFIG) -> dict[str, Any]:
    source_path = Path(path)
    data = json.loads(source_path.read_text(encoding="utf-8"))
    data.setdefault("filters", {})
    data.setdefault("sources", [])
    validate_source_config(data)
    return data


def validate_source_config(data: dict[str, Any]) -> None:
    seen: set[tuple[str, str]] = set()
    for item in data.get("sources", []):
        source_type = str(item.get("type", "")).lower()
        token = str(item.get("company", "")).strip()
        if source_type not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported job source type: {source_type}")
        if not token:
            raise ValueError("Every job source requires a company token")
        key = (source_type, token.lower())
        if key in seen:
            raise ValueError(f"Duplicate job source: {source_type}/{token}")
        seen.add(key)


def set_source_enabled(
    source_type: str,
    company: str,
    enabled: bool,
    path: str | Path = DEFAULT_SOURCE_CONFIG,
) -> dict[str, Any]:
    data = load_source_config(path)
    key = (source_type.lower(), company.lower())
    for item in data["sources"]:
        if (item["type"].lower(), item["company"].lower()) == key:
            item["enabled"] = bool(enabled)
            Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            return item
    raise KeyError(f"Job source not found: {source_type}/{company}")
