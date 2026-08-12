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

## Next: Profile review and local review queue

1. Resolve the short decision list in `docs/PROFILE_REVIEW.md` and issue a new
   profile version.
2. Add job review states: new, saved, dismissed, applied, interviewed, rejected.
3. Add personal labels: strong match, consider, weak match, reject, hard reject.
4. Build a small local review interface showing the job link, eligibility
   decision, exact reasons, and current experimental score.
5. Reevaluate stored jobs automatically when the profile version changes.
6. Measure precision at 10 and hard-reject leakage from real review labels.

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

Review the prepopulated profile's unresolved decisions, then build the local
review queue and feedback labels. This creates the real evaluation data needed
before semantic-weight tuning or Ollama reranking.
