import re
from typing import Dict


class JobNormalizer:
    """
    Converts structured job fields into a single clean embedding string.
    """

    def normalize(self, job: Dict[str, str]) -> str:
        text = f"""
        Title: {job.get('title', '')}
        Company: {job.get('company', '')}
        Location: {job.get('location', '')}
        Description: {job.get('description', '')}
        """

        return self._clean(text)

    def normalize_fields(self, job: Dict[str, str]) -> Dict[str, str]:
        """Return independently embeddable fields for weighted ranking."""

        return {
            "title": self._clean(job.get("title", "")) or "Unknown job title",
            "description": (
                self._clean(job.get("description", ""))
                or "No job description provided"
            ),
            "metadata": self._clean(
                f"Company: {job.get('company', '')} "
                f"Location: {job.get('location', '')}"
            ),
        }

    def _clean(self, text: str) -> str:
        # remove HTML tags if any
        text = re.sub(r"<[^>]+>", " ", text)

        # normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()
