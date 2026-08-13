# JobIntel Development Sprints

This backlog turns `BUILD_ROADMAP.md` into independently testable increments.
Sprint numbers describe dependency order, not calendar promises. A sprint is
complete only when its acceptance criteria and documentation are satisfied.

## Global definition of done

Every sprint must:

- preserve existing jobs, source attribution, eligibility history, and reviews;
- keep collection and deterministic screening operational with AI disabled;
- include migration and regression tests for changed persisted data;
- provide stable CLI/JSON operations where the feature may be automated;
- record enough version metadata to reproduce model-derived output;
- update the README, function map, and diagnostics when behavior changes;
- pass the full unit suite on a clean local database and an upgraded fixture.

## Sprint 0A — Scheduled-task benchmark

**Goal:** use the better-aligned scheduled high-fit search as the initial source
of positive benchmark candidates instead of treating the noisy broad queue as a
representative matching baseline.

### Implemented foundation

- Added a validated, idempotent JSON import command:
  `python -m backend.import_benchmark <file>`.
- Added migration-safe benchmark storage with task/run provenance, reported time,
  selection rationale, fit signals, concerns, and raw input.
- Scheduled results merge with an existing source posting without replacing the
  employer's complete description or review identity.
- Imported results remain unconfirmed (`new`, no match label) until Patrick
  reviews them.
- The dashboard identifies and filters benchmark candidates and displays the
  scheduled task's rationale.
- Benchmark candidates bypass the standard per-employer queue cap but remain
  subject to deterministic eligibility.

### Remaining work

- Import actual runs from the `High-fit leadership jobs` scheduled task.
- Have Patrick confirm or reject candidates with labels and reason codes.
- Add a command to export a de-identified, versioned evaluation snapshot.
- Record coverage, confirmed-positive rate, label distribution, hard-reject
  leakage, and reason frequency.
- Freeze confirmed candidates plus useful broad-queue negatives as the first
  regression baseline.

### Acceptance

- Imported results preserve direct employer links and task/run provenance.
- Re-importing one run creates no duplicate job or benchmark record.
- No scheduled-task recommendation becomes a positive label automatically.
- The baseline contains enough confirmed positives and useful negatives to
  distinguish retrieval quality; 20–30 reviewed examples remains the target,
  but they do not need to come from a random broad-queue slice.
- Baseline metrics can be reproduced from the exported snapshot.

### Dependency

None. Patrick's confirmation is required for completion. Sprint 1 can proceed
while scheduled-task candidates accumulate.

## Sprint 0B — Discovery parity

**Goal:** make JobIntel's independent hunting process find the genuinely suitable
jobs already found by the scheduled task.

### Implemented foundation

- Added `python -m backend.benchmark_report`.
- The report distinguishes pending, confirmed positive, and reviewed
  non-positive candidates.
- Confirmed-positive recall uses only `strong_match` and `consider` labels and
  reports independent sources, discovery timing, and missed confirmed jobs.

### Work

- Validate parity on actual imported runs and freeze the first report.
- Search by responsibilities and role families rather than relying only on exact
  title keywords.
- Add broader public-web/employer-career-page discovery through a source contract
  that preserves direct links and source health.
- Track unique relevant yield by source and avoid re-reporting reviewed jobs.

### Acceptance

- Discovery parity is reproducible from stored benchmark and discovery records.
- Missed benchmark jobs are visible with a reason when determinable.
- A new source is retained only when it contributes measurable unique relevant
  jobs without weakening failure isolation.
- Collection volume is never reported as matching quality.

### Dependency

Enough confirmed Sprint 0A candidates to measure meaningful recall.

## Sprint 1 — Candidate Intelligence Foundation

**Goal:** create the durable input contract used by filters, models, agents, and
application generation.

### Work

- Add stable evidence IDs and provenance for achievements, skills, education,
  role history, preferences, and organization-fit/personality statements.
- Define and validate a versioned Job Fit Specification schema.
- Migrate the current profile without losing profile version `2026-08-12.2`.
- Add commands to generate a draft fit spec, validate it, show a semantic diff,
  approve/activate a version, and import/export JSON.
- Ensure the active specification explicitly separates hard rules, ranking
  preferences, culture/personality signals, and uncertainty policy.
- Add an audit trail linking an approved spec to its source profile/evidence.

### Acceptance

- Every career claim has a unique stable evidence ID and source/provenance field.
- The migrated active spec reproduces all current deterministic decisions.
- An unapproved generated spec cannot affect screening or ranking.
- Export/import round-trips without information loss.
- Invalid IDs, conflicting rules, and unsupported schema versions fail clearly.

### Suggested implementation areas

- `backend/profile/`
- `backend/storage/database.py`
- `backend/storage/job_store.py`
- `data/input/Profiles/`
- new `backend/fit_spec/`

## Sprint 2 — Model Gateway and Ollama Adapter

**Goal:** make AI replaceable and locally runnable through stable task contracts.

### Work

- Define provider-neutral request/result envelopes and task-specific JSON schemas.
- Implement `disabled`, deterministic test, and Ollama providers.
- Configure provider, model, context, timeout, retry, and concurrency centrally.
- Persist provider/model/prompt/schema versions, inputs or input hashes, outputs,
  validation failures, duration, and retry count.
- Add health, list-models, and single-task CLI commands.
- Add repair/retry handling for malformed output without accepting partial data.

### Acceptance

- The same contract tests pass for the deterministic and Ollama adapters.
- With Ollama stopped, collection, eligibility, review, and export still work.
- Unknown fields, malformed JSON, and unknown evidence IDs are rejected.
- A different provider can be added without changing domain services or schemas.
- Diagnostics clearly distinguishes disabled, unavailable, unhealthy, and ready.

### Dependency

Sprint 1 schemas and evidence IDs.

## Sprint 3 — Job Understanding and First-stage Retrieval

**Goal:** convert long postings into structured, searchable facts and a bounded
shortlist that does not require an LLM for every job.

### Work

- Preserve section-aware chunks for long descriptions.
- Extract deterministic fields where reliable, then use the model gateway for
  structured responsibilities, requirements, preferences, and organization cues.
- Store extraction results by job-content and schema version.
- Build facet comparisons for title/role family, seniority, skills, experience,
  compensation, location, employment type, travel, and credentials.
- Produce a configurable shortlist for deeper analysis.

### Acceptance

- No required/preferred section in the test corpus is lost to context truncation.
- Changed job text invalidates only affected derived analysis.
- Cached extraction avoids duplicate model calls for unchanged content.
- Hard-ineligible jobs never enter the shortlist.
- Shortlist recall is measured against the Sprint 0 benchmark before thresholds are
  accepted.

### Dependency

Sprints 0A–2. Sprint 0B informs source recall but does not block job-text work.

## Sprint 4 — Evidence-grounded Fit Analysis and Model Benchmark

**Goal:** explain why a job fits, what is missing, and how confident the system
should be without inventing candidate experience.

### Work

- Map each job requirement to `met`, `partial`, `missing`, or `uncertain`.
- Require valid evidence IDs for `met` and `partial` findings.
- Produce gaps, disqualifiers, organization-fit signals, risks, confidence, and
  recommendation in structured output.
- Add review UI for explanations and model feedback.
- Benchmark candidate local models on the frozen labeled jobs.
- Tune shortlist/ranking thresholds only from measured results.

### Acceptance

- Zero accepted candidate claims reference missing/unknown evidence IDs.
- Unsupported-claim rate, precision at 10, hard-reject leakage, latency, and
  memory use are reported for each tested model.
- Analysis is reproducible from stored versions and inputs.
- Patrick can correct a finding without changing the original job or evidence.
- The chosen default model meets documented quality/resource thresholds; if none
  does, the system stays in deterministic/manual-review mode.

### Dependency

Sprints 0–3.

## Sprint 5 — Application Studio

**Goal:** prepare a reviewable, truthful application package for a selected job.

### Work

- Add `Prepare application` in the dashboard and an equivalent CLI command.
- Build and display a requirement-to-evidence plan before drafting.
- Generate an ATS-safe resume variant, cover letter, short-answer bank, and
  evidence matrix from approved evidence only.
- Add claim validation, editable drafts, revision history, and approval states.
- Export a predictable local package with machine-readable manifest.

### Acceptance

- Every non-generic candidate claim maps to one or more valid evidence IDs.
- Missing evidence becomes an explicit gap, never fabricated prose.
- Regeneration creates a new revision and never overwrites canonical evidence.
- Package manifest records job, fit spec, evidence, provider, model, prompt,
  schema, and document versions.
- A complete package remains viewable/exportable after AI is disabled.

### Dependency

Sprint 4.

## Sprint 6 — Unattended Pipeline and Windows Operations

**Goal:** run discovery and analysis reliably without an interactive agent.

### Work

- Add one idempotent pipeline command with collection-only, AI-disabled, and
  full-analysis modes.
- Add safe install/status/remove commands for Windows Task Scheduler.
- Persist run steps, logs, durations, failures, retry state, and final summary.
- Add provider-offline fallback and bounded retries/backoff.
- Add verified SQLite/document backup and restore instructions.
- Surface last run and actionable failures in the dashboard.

### Acceptance

- Two consecutive runs create no duplicate jobs, analyses, or packages.
- A failed source cannot expire its jobs; a failed model cannot fail collection.
- The next run safely resumes incomplete analysis work.
- Scheduler install/remove is repeatable and does not modify unrelated tasks.
- Backup verification proves that reviews, analyses, and application history can
  be restored.

### Dependency

Sprints 2–5. Collection-only scheduler work may begin earlier.

## Sprint 7 — Source Quality and Local-market Expansion

**Goal:** improve unique high-fit yield, especially within 30 miles of Sandy,
without adding brittle or low-value sources.

### Work

- Measure source-level unique jobs, reviewable yield, high-fit yield, staleness,
  duplicates, and failures.
- Evaluate a true Utah/local-market source using the same source contract.
- Add source budgets, health thresholds, and disable/review recommendations.
- Retain direct ATS boards as high-quality supplemental sources.

### Acceptance

- Any added source contributes measured unique relevant jobs in a live trial.
- Local results enforce Patrick's 30-mile geography without requiring relocation.
- Missing credentials or paid access never block existing no-key sources.
- Source failures remain isolated and visible.

### Dependency

May begin after Sprint 0A; prioritize after the main intelligence pipeline works.

## Sprint 8 — Agent Interoperability and Release Hardening

**Goal:** let any capable agent operate the live system through documented,
stable interfaces while keeping the system independently runnable.

### Work

- Document CLI and JSON contracts for status, collect, evaluate, shortlist,
  analyze, prepare application, export, and backup.
- Add machine-readable command help, exit codes, and dry-run behavior.
- Add end-to-end upgrade, provider-offline, and recovery tests.
- Remove hidden dependencies on developer-specific paths, chats, or credentials.
- Produce a Windows release checklist and operator runbook.

### Acceptance

- A clean machine can install, diagnose, collect, review, and run in AI-disabled
  mode using repository documentation alone.
- An agent can discover supported operations without reading implementation code.
- Optional hosted-provider credentials are isolated and absent by default.
- The release checklist passes on the target Windows machine.

### Dependency

Sprints 1–7.

## Recommended next-session ticket order

1. `S0A-02` Import the first actual scheduled-task run.
2. `S0A-03` Confirm/reject benchmark candidates in the dashboard.
3. `S0A-04` Baseline snapshot export and metrics.
4. `S0B-02` Validate and freeze discovery parity on actual benchmark runs.
5. `S1-01` Evidence ID/provenance schema.
6. `S1-02` Job Fit Specification JSON schema and validator.
7. `S1-03` Migration of profile `2026-08-12.2`.
8. `S1-04` Draft/approve/activate/diff/import/export commands.
9. `S1-05` Regression tests proving deterministic equivalence.

Do not start model selection with `S2` until Sprint 0A data and Sprint 1
contracts exist. The model is an implementation choice; the schemas and evidence
rules are the durable product.
