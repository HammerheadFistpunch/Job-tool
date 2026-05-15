import requests
from typing import List, Dict


class GreenhouseFetcher:
    """
    Fetches jobs from Greenhouse public job boards.
    """

    def __init__(self, company: str):
        self.company = company
        self.url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    def fetch(self) -> List[Dict]:
        response = requests.get(self.url)
        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data.get("jobs", []):
            jobs.append({
                "id": str(job.get("id", "")),
                "title": job.get("title", ""),
                "company": self.company,
                "location": job.get("location", {}).get("name", ""),
                "description": job.get("content", ""),
                "source": "greenhouse"
            })

        return jobs
