"""Validated, AI-independent candidate profile types."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def _strings(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be a list of strings")
    return value


@dataclass(frozen=True)
class LocationRules:
    home_city: str
    home_state: str
    max_distance_miles: int
    remote_accepted: bool
    relocation_accepted: bool
    accepted_localities: list[str] = field(default_factory=list)
    missing_location: str = "needs_review"


@dataclass(frozen=True)
class CompensationRules:
    absolute_base_floor: int
    target_base_min: int
    target_base_max: int
    missing_salary: str = "needs_review"


@dataclass(frozen=True)
class CandidateProfile:
    profile_version: str
    professional_name: str
    location: LocationRules
    compensation: CompensationRules
    target_titles: list[str]
    adjacent_titles: list[str]
    excluded_title_patterns: list[str]
    hard_rejection_phrases: dict[str, list[str]]
    preferred_organization_traits: list[str]
    demonstrated_skills: list[str]
    education: list[str]
    work_history: list[dict[str, Any]]
    unresolved_decisions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CandidateProfile":
        required = ("profile_version", "professional_name", "location", "compensation")
        missing = [name for name in required if name not in data]
        if missing:
            raise ValueError(f"Profile is missing required fields: {', '.join(missing)}")

        location_data = data["location"]
        compensation_data = data["compensation"]
        if not isinstance(location_data, dict) or not isinstance(compensation_data, dict):
            raise ValueError("location and compensation must be objects")

        valid_missing = {"eligible", "needs_review", "ineligible"}
        location = LocationRules(**location_data)
        compensation = CompensationRules(**compensation_data)
        if location.missing_location not in valid_missing:
            raise ValueError("location.missing_location has an invalid decision")
        if compensation.missing_salary not in valid_missing:
            raise ValueError("compensation.missing_salary has an invalid decision")
        if compensation.absolute_base_floor > compensation.target_base_min:
            raise ValueError("absolute salary floor cannot exceed target minimum")
        if compensation.target_base_min > compensation.target_base_max:
            raise ValueError("target salary minimum cannot exceed target maximum")

        hard_rejections = data.get("hard_rejection_phrases", {})
        if not isinstance(hard_rejections, dict):
            raise ValueError("hard_rejection_phrases must be an object")
        for name, phrases in hard_rejections.items():
            _strings(phrases, f"hard_rejection_phrases.{name}")

        work_history = data.get("work_history", [])
        if not isinstance(work_history, list) or not all(
            isinstance(item, dict) for item in work_history
        ):
            raise ValueError("work_history must be a list of objects")

        return cls(
            profile_version=str(data["profile_version"]),
            professional_name=str(data["professional_name"]),
            location=location,
            compensation=compensation,
            target_titles=_strings(data.get("target_titles", []), "target_titles"),
            adjacent_titles=_strings(data.get("adjacent_titles", []), "adjacent_titles"),
            excluded_title_patterns=_strings(data.get("excluded_title_patterns", []), "excluded_title_patterns"),
            hard_rejection_phrases=hard_rejections,
            preferred_organization_traits=_strings(data.get("preferred_organization_traits", []), "preferred_organization_traits"),
            demonstrated_skills=_strings(data.get("demonstrated_skills", []), "demonstrated_skills"),
            education=_strings(data.get("education", []), "education"),
            work_history=work_history,
            unresolved_decisions=_strings(data.get("unresolved_decisions", []), "unresolved_decisions"),
        )
