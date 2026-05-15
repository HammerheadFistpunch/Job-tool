import requests
from typing import List, Dict


class GreenhouseFetcher:
    def __init__(self, company: str):
        self.company = company
        self.url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

    def fetch(self) -> List[Dict]:
        try:
            response = requests.get(self.url, timeout=10)

            if response.status_code != 200:
                return []

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

        except Exception:
            return []