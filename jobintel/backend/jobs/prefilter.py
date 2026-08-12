"""Cheap market-scope filter applied before jobs enter the database."""

from __future__ import annotations

import re
from typing import Any


def _matches_any(text: str, terms: list[str]) -> bool:
    return any(re.search(rf"\b{re.escape(term.lower())}\b", text) for term in terms)


class MarketPrefilter:
    def __init__(self, settings: dict[str, Any] | None = None):
        self.settings = settings or {}

    def accepts(self, job: dict[str, Any]) -> bool:
        if not self.settings.get("enabled", True):
            return True
        title = str(job.get("title") or "").lower()
        location = str(job.get("location") or "").lower()
        title_terms = self.settings.get("title_terms", [])
        excluded_titles = self.settings.get("excluded_title_terms", [])
        location_terms = self.settings.get("location_terms", [])
        if excluded_titles and _matches_any(title, excluded_titles):
            return False
        if title_terms and not _matches_any(title, title_terms):
            return False
        return not location_terms or _matches_any(location, location_terms)

    def filter(self, jobs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
        accepted = [job for job in jobs if self.accepts(job)]
        return accepted, len(jobs) - len(accepted)
