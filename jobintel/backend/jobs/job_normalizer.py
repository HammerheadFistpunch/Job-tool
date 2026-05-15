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

    def _clean(self, text: str) -> str:
        # remove HTML tags if any
        text = re.sub(r"<[^>]+>", " ", text)

        # normalize whitespace
        text = re.sub(r"\s+", " ", text)

        return text.strip()
