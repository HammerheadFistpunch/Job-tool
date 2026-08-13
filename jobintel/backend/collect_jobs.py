"""Collect and persist jobs without loading any AI models.

Run with: ``python -m backend.collect_jobs``
"""

import logging

from backend.jobs.job_aggregator import JobAggregator
from backend.jobs.job_ingestion import JobIngestionPipeline
from backend.storage.job_store import JobStore


def collect() -> tuple[int, int]:
    aggregator = JobAggregator()

    with JobStore() as store:
        run_id = store.start_collection_run()
        try:
            raw_jobs, errors, reports = aggregator.fetch_all_jobs_with_report()
            jobs = JobIngestionPipeline().load_from_list(raw_jobs)
            summary = store.upsert_jobs(jobs)
            for report in reports:
                if report["status"] == "success":
                    report["expired"] = store.expire_missing_from_source(
                        report["source"], report.get("scope") or report["company"],
                        report["external_ids"]
                    )
                    summary.expired += report["expired"]
            store.record_source_results(run_id, reports)
            store.finish_collection_run(run_id, summary, errors)
        except Exception as error:
            store.fail_collection_run(run_id, error)
            raise

    print(
        "Collection complete: "
        f"{summary.fetched} fetched, {summary.created} new, "
        f"{summary.updated} updated, {summary.unchanged} unchanged, "
        f"{summary.expired} expired, {len(errors)} source errors."
    )
    for error in errors:
        print(
            f"[WARN] {error.get('source')} {error.get('company')}: "
            f"{error.get('error')}"
        )
    return summary.fetched, len(errors)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    fetched, errors = collect()
    return 1 if fetched == 0 and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
