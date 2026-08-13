"""Validated import of scheduled-scout results into the durable JobIntel store."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.storage.job_store import JobStore


class BenchmarkImportError(ValueError):
    """Raised when a benchmark file cannot be safely imported."""


def _required_text(value: Any, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise BenchmarkImportError(f"Missing required field: {field}")
    return text


def _string_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise BenchmarkImportError(f"{field} must be a list of strings")
    return [item.strip() for item in value if item.strip()]


def _timestamp(value: Any, field: str) -> str:
    text = _required_text(value, field)
    try:
        datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise BenchmarkImportError(f"{field} must be an ISO-8601 timestamp") from error
    return text


def _job_url(value: Any, field: str) -> str:
    text = _required_text(value, field)
    parts = urlsplit(text)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise BenchmarkImportError(f"{field} must be an absolute http(s) URL")
    return text


def _external_id(url: str) -> str:
    digest = hashlib.sha256(url.strip().lower().encode("utf-8")).hexdigest()[:24]
    return f"scheduled-{digest}"


class BenchmarkImporter:
    """Imports recommendations as candidates, never as confirmed positive labels."""

    source = "scheduled_task"

    def __init__(self, database: str | Path | None = None):
        self.database = database

    def import_file(self, path: str | Path) -> dict[str, Any]:
        input_path = Path(path)
        try:
            payload = json.loads(input_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise BenchmarkImportError(f"Unable to read benchmark JSON: {error}") from error
        result = self.import_payload(payload)
        result["input_file"] = str(input_path.resolve())
        return result

    def import_payload(self, payload: Any) -> dict[str, Any]:
        if not isinstance(payload, dict):
            raise BenchmarkImportError("Benchmark input must be a JSON object")

        task_id = _required_text(payload.get("task_id"), "task_id")
        task_name = str(payload.get("task_name") or "").strip()
        task_run_id = _required_text(payload.get("task_run_id"), "task_run_id")
        reported_at = _timestamp(payload.get("reported_at"), "reported_at")
        raw_jobs = payload.get("jobs")
        if not isinstance(raw_jobs, list) or not raw_jobs:
            raise BenchmarkImportError("jobs must be a non-empty list")

        normalized: list[dict[str, Any]] = []
        metadata: list[dict[str, Any]] = []
        for index, raw_job in enumerate(raw_jobs):
            prefix = f"jobs[{index}]"
            if not isinstance(raw_job, dict):
                raise BenchmarkImportError(f"{prefix} must be an object")
            canonical_url = _job_url(raw_job.get("canonical_url"), f"{prefix}.canonical_url")
            rationale = _required_text(
                raw_job.get("selection_rationale"), f"{prefix}.selection_rationale"
            )
            job_reported_at = _timestamp(
                raw_job.get("reported_at") or reported_at, f"{prefix}.reported_at"
            )
            external_id = _external_id(canonical_url)
            fit_signals = _string_list(raw_job.get("fit_signals"), f"{prefix}.fit_signals")
            concerns = _string_list(raw_job.get("concerns"), f"{prefix}.concerns")
            normalized.append({
                "external_id": external_id,
                "source": self.source,
                "company": _required_text(raw_job.get("company"), f"{prefix}.company"),
                "title": _required_text(raw_job.get("title"), f"{prefix}.title"),
                "location": str(raw_job.get("location") or "").strip(),
                "description": str(raw_job.get("description") or "").strip(),
                "canonical_url": canonical_url,
                "posted_at": str(raw_job.get("posted_at") or "").strip(),
                "updated_at": str(raw_job.get("updated_at") or "").strip(),
                "discovery_scope": task_id,
                "query_name": task_name or task_id,
                "location_scope": str(raw_job.get("location_scope") or "").strip(),
                "raw": raw_job,
            })
            metadata.append({
                "external_id": external_id,
                "reported_at": job_reported_at,
                "selection_rationale": rationale,
                "fit_signals": fit_signals,
                "concerns": concerns,
                "raw": raw_job,
            })

        jobs = JobIngestionPipeline().load_from_list(normalized)
        with JobStore(self.database) as store:
            summary = store.upsert_jobs(jobs)
            for item in metadata:
                job_id = store.job_id_for_discovery(
                    self.source, item["external_id"], task_id
                )
                store.save_benchmark_candidate(
                    job_id,
                    task_id=task_id,
                    task_name=task_name,
                    task_run_id=task_run_id,
                    reported_at=item["reported_at"],
                    selection_rationale=item["selection_rationale"],
                    fit_signals=item["fit_signals"],
                    concerns=item["concerns"],
                    raw=item["raw"],
                )

        return {
            "task_id": task_id,
            "task_run_id": task_run_id,
            "candidates": len(jobs),
            "created": summary.created,
            "updated": summary.updated,
            "unchanged": summary.unchanged,
        }
