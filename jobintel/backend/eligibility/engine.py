"""Explainable hard filters that run before semantic or LLM ranking."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from backend.profile.schema import CandidateProfile


@dataclass(frozen=True)
class DecisionReason:
    code: str
    decision: str
    explanation: str
    evidence: str = ""


@dataclass(frozen=True)
class EligibilityDecision:
    status: str
    reasons: list[DecisionReason]

    def to_dict(self) -> dict[str, Any]:
        return {"status": self.status, "reasons": [asdict(reason) for reason in self.reasons]}


class EligibilityEvaluator:
    def __init__(self, profile: CandidateProfile):
        self.profile = profile

    def evaluate(self, job: dict[str, Any]) -> EligibilityDecision:
        title = str(job.get("title") or "").strip()
        location = str(job.get("location") or "").strip()
        description = str(job.get("description") or "").strip()
        combined = f"{title}\n{location}\n{description}".lower()
        reasons: list[DecisionReason] = []
        reasons.extend(self._hard_phrases(combined))
        reasons.extend(self._title(title))
        reasons.extend(self._location(location))
        reasons.extend(self._salary(combined))

        status = "eligible"
        if any(reason.decision == "ineligible" for reason in reasons):
            status = "ineligible"
        elif any(reason.decision == "needs_review" for reason in reasons):
            status = "needs_review"
        else:
            reasons.append(DecisionReason(
                "no_hard_filter_triggered", "eligible",
                "No deterministic exclusion or unresolved eligibility condition was found.",
            ))
        return EligibilityDecision(status, reasons)

    def _hard_phrases(self, text: str) -> list[DecisionReason]:
        reasons = []
        for rule, phrases in self.profile.hard_rejection_phrases.items():
            for phrase in phrases:
                if phrase.lower() in text:
                    reasons.append(DecisionReason(
                        rule, "ineligible", f"Hard-rejection rule triggered: {rule}.", phrase
                    ))
                    break
        return reasons

    def _title(self, title: str) -> list[DecisionReason]:
        normalized = title.lower()
        for pattern in self.profile.excluded_title_patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return [DecisionReason(
                    "excluded_title", "ineligible",
                    "The title matches an explicitly excluded role pattern.", title,
                )]
        return []

    def _location(self, location: str) -> list[DecisionReason]:
        rules = self.profile.location
        if not location:
            return [DecisionReason(
                "location_missing", rules.missing_location,
                "The posting does not provide enough location information.",
            )]
        normalized = location.lower()
        if "remote" in normalized and rules.remote_accepted:
            if re.search(r"\b(us|u\.s\.|usa|united states|utah)\b", normalized) or normalized == "remote":
                return []
            return [DecisionReason(
                "remote_region_uncertain", "needs_review",
                "The role is remote, but its permitted hiring region is unclear.", location,
            )]
        if any(
            normalized == place.lower()
            or (
                re.search(rf"\b{re.escape(place.lower())}\b", normalized)
                and re.search(r"\b(ut|utah)\b", normalized)
            )
            for place in rules.accepted_localities
        ):
            return []
        if re.search(r"\b(ut|utah)\b", normalized):
            return [DecisionReason(
                "distance_requires_review", "needs_review",
                f"The Utah location requires distance verification against the {rules.max_distance_miles}-mile limit.",
                location,
            )]
        if not rules.relocation_accepted:
            return [DecisionReason(
                "relocation_required", "ineligible",
                "The role is outside the accepted local area and relocation is not accepted.", location,
            )]
        return []

    def _salary(self, text: str) -> list[DecisionReason]:
        ranges = self._annual_salary_ranges(text)
        if not ranges:
            return [DecisionReason(
                "salary_missing", self.profile.compensation.missing_salary,
                "No reliable annual base-salary range was found.",
            )]
        highest_posted_max = max(maximum for _minimum, maximum, _evidence in ranges)
        if highest_posted_max < self.profile.compensation.absolute_base_floor:
            evidence = max(ranges, key=lambda item: item[1])[2]
            return [DecisionReason(
                "salary_below_floor", "ineligible",
                f"The posted maximum base salary is below ${self.profile.compensation.absolute_base_floor:,}.",
                evidence,
            )]
        return []

    @staticmethod
    def _annual_salary_ranges(text: str) -> list[tuple[int, int, str]]:
        pattern = re.compile(
            r"\$\s*(\d{2,3}(?:,\d{3})?|\d{5,6}|\d{2,3}(?:\.\d+)?\s*k)\s*"
            r"(?:-|–|—|to)\s*\$?\s*(\d{2,3}(?:,\d{3})?|\d{5,6}|\d{2,3}(?:\.\d+)?\s*k)",
            re.IGNORECASE,
        )

        def amount(value: str) -> int:
            cleaned = value.lower().replace(",", "").replace(" ", "")
            return int(float(cleaned[:-1]) * 1000) if cleaned.endswith("k") else int(cleaned)

        results = []
        for match in pattern.finditer(text):
            minimum, maximum = amount(match.group(1)), amount(match.group(2))
            context = text[max(0, match.start() - 50):match.end() + 50]
            nearby = text[match.end():match.end() + 30]
            if re.search(r"/(?:hr|hour)|per hour|hourly", nearby, re.IGNORECASE):
                continue
            if maximum >= 10_000 and re.search(
                r"salary|base pay|base compensation|compensation range|annual pay|per year|annually",
                context,
                re.IGNORECASE,
            ):
                results.append((minimum, maximum, match.group(0)))
        return results
