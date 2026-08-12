"""Central settings with environment-variable overrides."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


DEFAULT_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"


def load_settings(path: str | Path | None = None) -> dict[str, Any]:
    settings_path = Path(path) if path else DEFAULT_PATH
    data = json.loads(settings_path.read_text(encoding="utf-8"))
    overrides: dict[tuple[str, str], tuple[str, Any]] = {
        ("dashboard", "host"): ("JOBINTEL_HOST", str),
        ("dashboard", "port"): ("JOBINTEL_PORT", int),
        ("embedding", "model"): ("JOBINTEL_EMBEDDING_MODEL", str),
        ("ollama", "url"): ("JOBINTEL_OLLAMA_URL", str),
        ("ollama", "model"): ("JOBINTEL_OLLAMA_MODEL", str),
        ("ollama", "context_size"): ("JOBINTEL_OLLAMA_CONTEXT", int),
    }
    for (section, key), (environment, converter) in overrides.items():
        value = os.getenv(environment)
        if value is not None:
            data[section][key] = converter(value)
    if not 1 <= int(data["dashboard"]["port"]) <= 65535:
        raise ValueError("dashboard.port must be between 1 and 65535")
    if int(data["ollama"]["context_size"]) < 1024:
        raise ValueError("ollama.context_size must be at least 1024")
    return data
