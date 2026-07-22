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

## Next: Structured candidate and eligibility model

1. Replace the single profile text blob with separate factual facets:
   demonstrated experience, accomplishments, tools, industries, education,
   target titles, adjacent titles, seniority, location, compensation, work
   arrangement, preferences, and hard exclusions.
2. Import factual career evidence from the existing profile and resume material.
3. Add deterministic filters for geography, remote policy, absolute salary
   floor, commission-only roles, junior/SDR roles, and required credentials.
4. Store filter decisions and explanations without deleting filtered jobs.
5. Add unit tests for every hard rule and ambiguous/missing source data.

## Then: Review queue and evaluation

1. Add job states: new, saved, dismissed, applied, interviewed, rejected.
2. Add personal labels: strong match, consider, weak match, reject, hard reject.
3. Build a small local review interface with job links and filter explanations.
4. Measure precision at 10, recall of strong matches, and hard-reject leakage.

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

Structured candidate facets and deterministic eligibility filters. This should
be completed before further tuning of semantic weights or skill extraction.
