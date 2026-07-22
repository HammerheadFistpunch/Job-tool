"""Shared job-domain types.

Database persistence is intentionally implemented in ``JobStore``. Keeping the
domain record independent of an ORM makes collection scripts and tests usable
before the web application stack is installed.
"""

from dataclasses import dataclass


@dataclass
class JobRecord:
    external_id: str
    source: str
    company: str
    title: str
    location: str = ""
    description: str = ""
    canonical_url: str = ""
    posted_at: str = ""
    updated_at: str = ""

