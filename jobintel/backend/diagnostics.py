"""Target-machine readiness report; never requires Ollama to be installed."""

from __future__ import annotations

import importlib.metadata
import json
import platform
import sqlite3
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from backend.config import load_settings
from backend.profile.loader import load_structured_profile
from backend.storage.database import connect_database, database_path, initialize_database


def _package(name: str) -> dict[str, str]:
    try:
        return {"status": "ok", "version": importlib.metadata.version(name)}
    except importlib.metadata.PackageNotFoundError:
        return {"status": "missing", "version": ""}


def _ollama(settings: dict[str, Any]) -> dict[str, Any]:
    url = settings["ollama"]["url"].rstrip("/") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            models = [item["name"] for item in json.load(response).get("models", [])]
        configured = settings["ollama"]["model"]
        return {"status": "ok", "models": models, "configured_model": configured,
                "configured_model_available": bool(configured and configured in models)}
    except (OSError, urllib.error.URLError, ValueError) as error:
        return {"status": "unavailable", "error": str(error), "configured_model": settings["ollama"]["model"]}


def run_diagnostics() -> dict[str, Any]:
    settings = load_settings()
    connection = connect_database()
    try:
        initialize_database(connection)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    finally:
        connection.close()
    profile = load_structured_profile()
    return {
        "overall": "ready_for_non_llm_work",
        "platform": {"system": platform.system(), "release": platform.release(), "python": sys.version.split()[0]},
        "database": {"path": str(database_path()), "integrity": integrity, "tables": sorted(tables)},
        "profile": {"version": profile.profile_version, "unresolved_decisions": profile.unresolved_decisions},
        "packages": {name: _package(name) for name in ("fastapi", "uvicorn", "sentence-transformers", "ollama")},
        "settings": settings,
        "ollama": _ollama(settings),
    }


if __name__ == "__main__":
    report = run_diagnostics()
    output = Path("jobintel-readiness.json")
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nSaved readiness report: {output.resolve()}")
