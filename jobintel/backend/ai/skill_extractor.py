import re
from typing import List, Dict


class SkillExtractor:
    """
    Source-of-truth signal extractor.

    Key principle:
    - DO NOT impose a fixed skill taxonomy
    - Extract what actually exists in text
    """

    def __init__(self):

        # minimal normalization only (not a full ontology)
        self.normalization_map = {
            "js": "javascript",
            "nodejs": "javascript",
            "ml": "machine learning",
            "ai": "ai",
            "aws": "aws",
            "gcp": "gcp",
            "postgresql": "sql",
            "mysql": "sql"
        }

        # patterns for weak structure detection
        self.patterns = [
            r"\bpython\b",
            r"\bjavascript\b",
            r"\bjava\b",
            r"\bsql\b",
            r"\baws\b",
            r"\bgcp\b",
            r"\bazure\b",
            r"\bdocker\b",
            r"\bkubernetes\b",
            r"\bapi\b",
            r"\bbackend\b",
            r"\bfrontend\b",
            r"\bdata\b",
            r"\bmachine learning\b",
            r"\bai\b",
            r"\bllm\b",
            r"\bgenai\b",
            r"\bproduct\b",
            r"\bdesign\b",
            r"\bstrategy\b",
            r"\boperations\b"
        ]

    def _normalize(self, token: str) -> str:
        return self.normalization_map.get(token, token)

    def extract(self, text: str) -> List[str]:
        if not text:
            return []

        text_lower = text.lower()

        found = set()

        # 1. direct evidence extraction (source-of-truth)
        for pattern in self.patterns:
            matches = re.findall(pattern, text_lower)
            for m in matches:
                found.add(self._normalize(m))

        # 2. keep only what actually appears
        return sorted(found)