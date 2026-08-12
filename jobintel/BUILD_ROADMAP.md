# JobIntel Build Roadmap

## Goal

Build an automated, local-first job intelligence system optimized for:

1. Reliable unattended collection.
2. High-quality personal job matching.
3. Evidence-based local LLM analysis through Ollama.
4. Measurable improvement from Patrick's review decisions.

## Completed: Collection foundation

- Full Greenhouse descriptions, URLs, IDs, locations, and update dates.
- Lever feed support.
- Configurable ATS sources.
- Retries and visible source errors.
- SQLite persistence and non-destructive legacy schema upgrade.
- Source-aware deduplication and content-change detection.
- First-seen and last-seen tracking.
- Collection run history.
- AI-independent collection command suitable for scheduling.
- Unit coverage for complete records, errors, deduplication, updates, and runs.

## Completed: Data-definition preparation

- Added `docs/JOB_TOOL_DATA_INTAKE.md`, a human-editable worksheet separating
  eligibility rules, ranking preferences, candidate evidence, and job inputs.
- Added `docs/JOB_TOOL_FUNCTION_MAP.md`, with editable Mermaid architecture
  diagrams, component status, database flow, and the planned end state.
- Established a conservative missing-data rule: ambiguous eligibility data
  should normally produce `needs_review`, not an automatic rejection.
- Deferred profile assumptions until Patrick completes the worksheet and
  supplies the resume/job evidence to structure.

## Completed: Structured candidate and eligibility foundation

- Added a validated, versioned JSON candidate profile populated from known
  preferences, resume facts, education, skills, and work history.
- Added deterministic filters for location/relocation, remote regions, annual
  salary floor, commission-only work, primary cold-calling, forced overtime,
  and excluded junior sales/SDR titles.
- Added `eligible`, `needs_review`, and `ineligible` results with exact evidence.
- Added profile-versioned SQLite evaluation storage without deleting jobs.
- Integrated eligibility into recommendations so hard rejects never reach
  semantic ranking.
- Added unit tests for hard rules, ambiguous data, profile validation, and
  evaluation persistence.

## Completed: Local review queue foundation

- Added SQLite-backed states: new, saved, dismissed, applied, interviewed,
  rejected.
- Added match labels: strong match, consider, weak match, reject, hard reject.
- Added consistent interest/rejection reason codes and free-text notes.
- Added a responsive local FastAPI review page with filters, source links,
  eligibility evidence, and posting text.
- Added automatic evaluation for new jobs, changed postings, and new profile
  versions before they enter the queue.
- Added API endpoints and service/storage tests.

## Completed: Initial profile-policy resolution

- No hard hybrid office-day maximum.
- Up to 25% routine travel accepted.
- Full-time, contract-to-hire, and fixed-term arrangements accepted.
- Missing salary treated as provisionally eligible.
- Missing required credentials require review unless legally mandatory.
- Senior individual-contributor roles rank equally with manager roles.
- Profile advanced to version `2026-08-12.2`; no unresolved decisions remain.

## Completed: Offline readiness foundation

- Added centralized settings and environment-variable overrides for the
  dashboard, schedule, embedding model, and future Ollama adapter.
- Added review metrics for coverage, label/state counts, reasons, precision at
  10, and hard-reject leakage.
- Added a reproducible 10-job policy fixture and validation command.
- Added diagnostics for Python, dependencies, SQLite integrity, profile state,
  configuration, Ollama availability, and installed models.
- Added safe Windows install, dashboard, and diagnostic launchers without yet
  registering background tasks.

## Completed: Expanded source collection

- Expanded the default registry from 3 to 20 candidate employers, with 14
  live-verified ATS boards enabled by default.
- Added configurable role and location prefiltering before database storage.
- Added per-board collection health, fetched/accepted/filtered counts, and a
  dashboard source-management panel.
- Added source-aware expiration that cannot close jobs when a board fails.
- Live smoke run retained 76 relevant postings across 9 employers with 14
  successful board checks; valid boards with zero current matches remain healthy.

## Current blocker: Employer-biased discovery

The target-machine run returned 77 active jobs, but the queue remained dominated
by Stripe, Airbnb, and Dropbox. The source-registry work is operationally sound,
but adding individual company boards does not provide broad market discovery.
This batch must not be used to tune matching or establish precision metrics.

## Next: Query-based market discovery

1. Add one or more broad sources that accept role and location queries across
   employers. Keep direct Greenhouse and Lever boards as supplemental sources.
2. Centralize configurable queries for target roles, remote-US work, and the
   Sandy/Salt Lake-area market.
3. Normalize broad-source results into the existing ingestion pipeline and
   deduplicate overlaps with direct ATS postings.
4. Preserve canonical links, provider attribution, query attribution, and raw
   source records.
5. Record per-query fetched/accepted/filtered/error counts, rate limits, and last
   successful collection.
6. Treat API-backed providers as optional integrations. Missing keys or provider
   outages must not stop ATS collection or eligibility evaluation.
7. Add tests for pagination, query construction, normalization, cross-source
   deduplication, partial failures, and safe expiration behavior.

### Discovery acceptance criteria

- A live collection contains at least 15 distinct employers.
- No single employer represents more than 20% of the reviewable queue.
- At least 30 reviewable jobs survive collection and deterministic eligibility.
- Remote-US and Utah-area searches are both represented in the collection
  report, even when one query yields zero matches.
- Every enabled source/query reports success, failure, and result counts.
- Repeated runs do not create duplicate jobs or erase review history.

## Then: Real-job evaluation baseline

1. Have Patrick label approximately 20–30 jobs from the diverse queue.
2. Surface the implemented summary metrics in the dashboard.
3. Measure precision at 10, hard-reject leakage, coverage, and reason frequency.
4. Use that measured baseline to redesign facet matching before Ollama reranking.

## Then: Matching quality

1. Chunk long descriptions so model token limits do not discard requirements.
2. Compare job fields to corresponding profile facets instead of one profile
   vector.
3. Combine title retrieval, description chunks, structured skills, and hard
   filters for a fast first-stage shortlist.
4. Tune scoring against labeled real jobs rather than arbitrary weights.

## Then: Ollama reranking

1. Add a model-agnostic Ollama adapter.
2. Analyze only the top 25–50 candidates from first-stage retrieval.
3. Require structured JSON with qualifications met, concrete candidate
   evidence, missing requirements, disqualifiers, recommendation, and confidence.
4. Reject unsupported claims that cannot point to stored career evidence.
5. Benchmark model quality, context size, speed, and VRAM usage on the target PC.

## Then: Operations and expansion

1. Add Windows scheduling setup, logs, retry policy, and failure notification.
2. Add import/export and database backup.
3. Expand sources only after their recommendation yield can be measured.
4. Add daily summaries and optional notifications.

## Current next build chunk

Implement query-based broad market discovery and meet the diversity acceptance
criteria above. Do not request user labels or tune matching until then.
