# Scheduled-task Benchmark Import

The existing scheduled `High-fit leadership jobs` search currently finds more
aligned jobs than JobIntel's broad keyword discovery. Its results should be used
as **benchmark candidates**, not automatically accepted as strong matches.

This import keeps the scheduled task as a temporary high-quality scout while
JobIntel remains the durable database, review system, and future local-model
workflow.

## Import command

From the `jobintel` directory:

```powershell
.venv\Scripts\python.exe -m backend.import_benchmark C:\path\to\benchmark.json
```

The importer validates the complete file before writing. Re-importing the same
task run is safe and does not duplicate jobs or benchmark records.

After review, print benchmark and discovery-parity metrics:

```powershell
.venv\Scripts\python.exe -m backend.benchmark_report
```

The report counts pending candidates, confirmed positives (`strong_match` or
`consider`), reviewed non-positives, confirmed jobs found independently by
JobIntel, recall, source overlap, discovery lag, and missed confirmed jobs.

## JSON contract

```json
{
  "task_id": "6a71342630608191bd0f7e426f17ccbb",
  "task_name": "High-fit leadership jobs",
  "task_run_id": "2026-08-13T08:00:00-06:00",
  "reported_at": "2026-08-13T08:05:00-06:00",
  "jobs": [
    {
      "title": "Director of Technical Marketing",
      "company": "Example Company",
      "location": "Remote - US",
      "description": "Complete posting text when available.",
      "canonical_url": "https://company.example/jobs/123",
      "posted_at": "2026-08-12T15:00:00Z",
      "selection_rationale": "Why the scheduled task surfaced this job.",
      "fit_signals": [
        "Technical translation",
        "Cross-functional leadership"
      ],
      "concerns": [
        "Travel percentage not stated"
      ],
      "location_scope": "remote_us"
    }
  ]
}
```

## Required fields

At the task-run level:

- `task_id`
- `task_run_id`: unique identifier for this run; an ISO timestamp is suitable
- `reported_at`: ISO-8601 timestamp
- `jobs`: non-empty list

For every job:

- `title`
- `company`
- `canonical_url`: direct absolute employer/application URL when available
- `selection_rationale`

Optional fields include `task_name`, `location`, `description`, `posted_at`,
`updated_at`, `fit_signals`, `concerns`, `location_scope`, and a per-job
`reported_at` override.

## Data behavior

- The scheduled result is stored with source `scheduled_task` and task-scoped
  provenance.
- Matching canonical URLs merge with an existing JobIntel posting and preserve
  its review history.
- A scheduled summary cannot replace a complete Greenhouse or Lever posting.
- The rationale, fit signals, concerns, original input, run ID, and report time
  are retained separately from the job posting.
- Imported candidates enter the dashboard as `new` with no match label.
- They remain subject to deterministic hard eligibility rules.
- They bypass the ordinary per-employer queue cap so the benchmark is visible.
- They are never expired merely because a later scheduled run does not repeat
  them; this preserves historical evaluation evidence.

## Review workflow

1. Open the dashboard.
2. Select **Scheduled-task benchmark** under discovery pools.
3. Read the task's rationale and the employer posting.
4. Assign Patrick's actual match label and reason codes.
5. Save the review.

The confirmed/rejected results will support discovery-parity measurement and the
future local-model benchmark. The standard broad queue remains useful for hard
filter and negative-example testing, but it is not the positive baseline.
