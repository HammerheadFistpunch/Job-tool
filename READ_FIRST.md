# READ FIRST — Job Job Development Handoff

This file is the source-of-truth pickup point for the next development session.
Read it before changing code. Then read `jobintel/BUILD_ROADMAP.md` for the
full implementation sequence.

## Verified repository state

- Repository: `HammerheadFistpunch/Job-tool`
- Working branch: `GPT_Redesign`
- Last verified functional commit before this handoff: `96e4a9425960f993da044b6170799e0c99145eb0`
- Local application folder: `jobintel`
- Candidate profile version: `2026-08-12.2`
- Target platform: Windows 11, Python 3.12.8, local SQLite, local Ollama

At the start of the next session, fetch the latest remote `GPT_Redesign` branch
and treat it as authoritative. Do not assume the commit above is still current.

## Current outcome

Job Job can reliably collect complete postings from configured Greenhouse and
Lever company boards, normalize and deduplicate them, preserve changes in
SQLite, apply explainable eligibility rules, and display the results in a local
review dashboard.

Query-based broad discovery is implemented through Jobicy's public remote-jobs
API alongside the direct ATS boards. A clean live validation on August 13, 2026
produced 107 distinct active jobs across 35 employers. The diversity-capped
review queue contained 56 eligible or needs-review jobs across 29 employers;
the largest employer represented 17.86%. All documented discovery acceptance
checks passed.

## What is working

- Greenhouse and Lever public ATS collection with retries and visible errors.
- Complete posting descriptions, links, source IDs, locations, and dates.
- SQLite persistence, source-aware deduplication, and posting change detection.
- Source-scoped expiration after a successful board fetch; failures cannot
  falsely close that board's jobs.
- A 20-employer registry with 14 live-verified boards enabled.
- Role/location prefiltering before storage.
- Per-board fetched, accepted, filtered, expired, and failure reporting.
- Dashboard source-health display and enable/disable controls.
- Versioned structured candidate profile with all initial choices resolved.
- Explainable `eligible`, `needs_review`, and `ineligible` decisions.
- Local FastAPI review queue with states, labels, reasons, notes, and job links.
- Review metrics API and a reproducible policy fixture.
- Windows setup, launch, and diagnostic scripts.
- Target-machine diagnostics: database, packages, and Ollama all reachable.
- Prior direct-board validation: 44 tests passed; a live smoke run completed all
  14 enabled boards with no errors and retained 76 prefiltered postings.
- Jobicy query discovery for technical marketing, product marketing, strategic
  communications, content strategy, creative/video, and Utah-area monitoring.
- Query-scoped attribution, health/count reporting, and safe expiration across
  overlapping providers.
- Cross-provider deduplication that preserves distinct same-provider openings.
- Configurable review-queue diversity cap that never deletes jobs or hides
  already-reviewed records.
- `python -m backend.discovery_report` acceptance report.
- Latest validation: 51 tests passed. Two consecutive live runs produced 107
  active jobs; the second run reported 0 new, 0 updated, and 134 unchanged
  discoveries while preserving a saved review marker.

## Known limitations

- The no-key broad provider is remote-focused. Its Utah-scoped query is recorded
  but returned zero local matches in the latest live run; a true local-market
  provider remains desirable later.
- The semantic embedding score remains experimental.
- Facet-based retrieval and long-description chunking are not built.
- Ollama reranking is not built or enabled.
- Background scheduling, notifications, backups, and a finished Windows
  installer are not built.
- Six candidate employer tokens are disabled after confirmed 404 responses;
  those employers may use different ATS products or private career APIs.

## Immediate next milestone

Run the new discovery build on Patrick's Windows database, confirm the generated
acceptance report, then have Patrick label approximately 20–30 jobs from the
diverse queue. Use those labels to establish precision at 10, hard-reject
leakage, coverage, and reason-frequency baselines before changing semantic
weights or beginning Ollama benchmarking.

## Restart procedure

From the repository root:

```powershell
git fetch origin
git switch GPT_Redesign
git pull --ff-only origin GPT_Redesign
cd jobintel
.venv\Scripts\python.exe -m backend.diagnostics
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe -m backend.collect_jobs
.venv\Scripts\python.exe -m backend.discovery_report
```

Before implementation, inspect:

- `READ_FIRST.md`
- `jobintel/BUILD_ROADMAP.md`
- `jobintel/config/job_sources.json`
- `jobintel/backend/jobs/job_aggregator.py`
- `jobintel/backend/jobs/prefilter.py`
- `jobintel/backend/storage/job_store.py`
- `jobintel/docs/JOB_TOOL_FUNCTION_MAP.md`

## Important design constraints

- Collection and deterministic eligibility must continue working without
  embeddings or Ollama.
- Missing or ambiguous eligibility data should normally produce
  `needs_review`, not a guessed rejection.
- Hard eligibility failures cannot be overridden by semantic or LLM scores.
- Never expire jobs because an external source failed.
- Keep all model and provider selections configurable rather than hard-coded.
- Store analysis model and prompt versions so results can be reproduced.
- Preserve existing jobs and Patrick's review history during schema upgrades.

## Next user checkpoint

Patrick can now run collection and the discovery report on the target machine.
If the report passes against his persistent database, review approximately
20–30 jobs in the dashboard. Do not tune ranking until those labels exist.
