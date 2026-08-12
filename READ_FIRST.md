# READ FIRST — Job Job Development Handoff

This file is the source-of-truth pickup point for the next development session.
Read it before changing code. Then read `jobintel/BUILD_ROADMAP.md` for the
full implementation sequence.

## Verified repository state

- Repository: `HammerheadFistpunch/Job-tool`
- Working branch: `GPT_Redesign`
- Last verified functional commit: `5d183936494531dc25b46f5c7fff8aac929664a1`
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

The current collection is **not yet broad enough to use as a matching
baseline**. A real run produced 77 active entries, still dominated by Stripe,
Airbnb, and Dropbox, with only a few jobs from other employers. Expanding a
static list from 3 to 20 candidate employers improved source management but did
not create market-wide discovery.

Do not ask Patrick to label the current batch. Its employer distribution is too
biased to support meaningful tuning.

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
- Latest functional validation: 44 tests passed; a live smoke run completed all
  14 enabled boards with no errors and retained 76 prefiltered postings.

## Known limitations

- Collection is still a finite list of individual employer boards, not a broad
  search of the available job market.
- The current queue is heavily employer-biased and unsuitable for evaluating
  match quality.
- The semantic embedding score remains experimental.
- Facet-based retrieval and long-description chunking are not built.
- Ollama reranking is not built or enabled.
- Background scheduling, notifications, backups, and a finished Windows
  installer are not built.
- Six candidate employer tokens are disabled after confirmed 404 responses;
  those employers may use different ATS products or private career APIs.

## Immediate next build milestone

Build query-based broad discovery while retaining individual ATS boards as
high-quality supplemental sources.

Required scope:

1. Add at least one broad, query-driven source that searches across employers.
2. Support configurable role queries for technical marketing, product
   marketing, strategic communications, content strategy, creative/video, and
   credible adjacent manager/director or senior-IC roles.
3. Support remote-US and Sandy/Salt Lake-area location queries.
4. Normalize broad-source records into the existing ingestion pipeline.
5. Deduplicate overlapping discoveries, including the same posting found through
   a broad source and a direct ATS board.
6. Preserve canonical job links and explicit source attribution.
7. Record per-query counts, failures, rate limits, and last successful run.
8. Make API-key-dependent providers optional; missing credentials must not stop
   direct ATS collection.
9. Add tests and a live collection report that demonstrates meaningful employer
   diversity before requesting user labels.

Acceptance criteria are defined in `jobintel/BUILD_ROADMAP.md`. Do not proceed
to matching-weight tuning or Ollama benchmarking until the discovery baseline
passes those criteria.

## Restart procedure

From the repository root:

```powershell
git fetch origin
git switch GPT_Redesign
git pull --ff-only origin GPT_Redesign
cd jobintel
.venv\Scripts\python.exe -m backend.diagnostics
.venv\Scripts\python.exe -m unittest discover -s tests -v
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

Patrick's next hands-on task should occur only after broad discovery produces a
diverse queue. At that point, ask him to review approximately 20–30 jobs so the
first real precision and rejection-leakage baseline can be measured.
