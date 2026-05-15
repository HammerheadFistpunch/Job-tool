from dataclasses import dataclass


@dataclass
class CandidateProfile:
    goals: list[str]
    strengths: list[str]
    preferred_roles: list[str]
    exclusions: list[str]
    work_preferences: list[str]