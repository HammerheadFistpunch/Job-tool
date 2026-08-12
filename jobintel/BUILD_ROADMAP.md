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

## Next: Real-job evaluation baseline

1. Run collection and review an initial set of real recommendations.
2. Add queue summary metrics: label counts, precision at 10, hard-reject
   leakage, and reasons by frequency.
3. Add a reproducible labeled-job evaluation fixture.
4. Use the measured baseline to redesign facet matching before Ollama reranking.

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

1. Add source-scoped expiration and job closure detection.
2. Add Windows scheduling setup, logs, retry policy, and failure notification.
3. Add import/export and database backup.
4. Expand sources only after their recommendation yield can be measured.
5. Add daily summaries and optional notifications.

## Current next build chunk

Collect and label an initial batch of real jobs in the review queue. Then add
baseline metrics before semantic-weight tuning or Ollama reranking.
