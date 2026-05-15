import json
from typing import List, Dict, Any


class JobIngestionPipeline:
    """
    Loads raw job data and converts it into a standardized format
    ready for normalization + embedding.
    """

    def __init__(self):
        self.jobs = []

    def load_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load jobs from a JSON file.
        Expected format: list of job dicts.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("Job JSON must be a list of job objects")

        self.jobs = [self._standardize(job) for job in data]
        return self.jobs

    def load_from_list(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Direct ingestion from Python list.
        Useful for API / scraping later.
        """
        self.jobs = [self._standardize(job) for job in jobs]
        return self.jobs

    def _standardize(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Forces consistent schema across all job inputs.
        Missing fields become empty strings.
        """

        return {
            "id": job.get("id", ""),
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "description": job.get("description", ""),
            "source": job.get("source", ""),
        }

    def get_jobs(self) -> List[Dict[str, Any]]:
        return self.jobs
