# JobIntel Build Roadmap

## Outcome

Build a local-first system that converts Patrick's career evidence, job-search
requirements, preferences, and organization-fit signals into a versioned filter;
hunts for matching jobs on a schedule; explains fit with traceable evidence; and
prepares application documents for approved jobs.

The system must remain useful without ChatGPT Premium. AI is a replaceable
capability behind stable contracts, not the owner of the workflow.

## Product layers

| Layer | Responsibility | AI required? | Current state |
|---|---|---:|---|
| Core | Collection, normalization, deduplication, persistence, hard rules, review state, export | No | Working |
| Candidate intelligence | Evidence library and approved Job Fit Specification | No after approval | Partially structured |
| Retrieval | Job chunking, facets, deterministic shortlist | No | Not built |
| Analysis | Requirement extraction, evidence comparison, organization-fit signals | Replaceable local/hosted model | Not built |
| Application studio | Evidence selection, resume/cover-letter drafts, package history | Replaceable model for drafting | Not built |
| Operations | Scheduling, logs, retries, backups, notifications | No | Partially ready |
| Agent interface | Stable CLI/JSON operations usable by any agent | No | Partial commands only |

## Architecture rules

1. **Local ownership.** SQLite and local files are the system of record.
2. **Deterministic first.** Hard eligibility and source lifecycle run before AI.
3. **Provider neutrality.** Model calls use task-specific request/response schemas
   and one adapter interface. Ollama is first; hosted adapters are optional.
4. **Evidence before prose.** Career claims have stable IDs and provenance.
   Analysis and application drafts must cite those IDs.
5. **Validated outputs.** Invalid JSON, unknown evidence IDs, or unsupported
   claims fail closed and enter retry/review; they never silently become facts.
6. **Reproducibility.** Store provider, model, prompt, schema, profile, fit-spec,
   and job-content versions for every analysis or generated package.
7. **Graceful degradation.** Provider outages cannot stop collection, screening,
   review, scheduling, or export.
8. **Human authority.** Patrick approves the fit specification and every
   application package. Automated submission is not in scope.

## Completed foundation

### Collection and market discovery

- Greenhouse, Lever, and query-based no-key Jobicy collection.
- Full descriptions, URLs, IDs, dates, locations, and raw source records.
- SQLite persistence, migration support, source-aware lifecycle, and run history.
- Cross-provider attribution and deduplication with safe expiration.
- Configurable role/location prefilter and source health reporting.
- Diverse review queue and `backend.discovery_report` acceptance checks.

### Deterministic candidate screening

- Versioned JSON candidate profile containing work history, skills, target roles,
  compensation, location, work rules, preferences, and exclusions.
- Explainable `eligible`, `needs_review`, and `ineligible` decisions.
- Hard rules for location, relocation, salary floor, commission-only work,
  primary cold calling, mandatory overtime, excluded titles, travel, employment
  arrangement, and credentials.
- Profile-versioned evaluation history. Hard failures never enter ranking.

### Review and readiness

- Local FastAPI queue with workflow states, labels, reasons, notes, and links.
- Coverage, precision-at-10, hard-reject leakage, and reason metrics.
- Reproducible policy fixture, diagnostics, settings, and Windows launchers.
- Latest validation: 51 tests and all broad-discovery acceptance checks passed.

## Delivery sequence

### Phase A — Trustworthy candidate intelligence

1. Capture 20–30 real-job labels and freeze the initial evaluation baseline.
2. Assign stable IDs and provenance to career achievements, skills, education,
   preferences, and personality/organization-fit statements.
3. Introduce a versioned Job Fit Specification separating:
   - hard eligibility rules;
   - preferred role families and seniority;
   - weighted ranking preferences;
   - organization/personality-fit signals;
   - negative signals and uncertainty policy.
4. Add generate, validate, diff, approve, activate, import, and export operations.
   A model may propose a specification, but only an approved version is active.

### Phase B — Provider-neutral local intelligence

1. Define model tasks and JSON schemas for job requirement extraction, job-fit
   analysis, and application drafting.
2. Add an AI provider protocol plus `disabled`, deterministic test, and Ollama
   adapters. Keep provider/model selection in configuration.
3. Persist task inputs, validated outputs, versions, latency, errors, and retries.
4. Add health checks and CLI commands that any agent or scheduler can invoke.

### Phase C — Job understanding and fit analysis

1. Chunk long postings without losing requirements or qualifications.
2. Extract structured responsibilities, required/preferred qualifications,
   compensation, work arrangement, travel, credentials, and organization cues.
3. Build a fast deterministic/facet shortlist before model analysis.
4. Compare each shortlisted requirement with cited candidate evidence.
5. Produce fit, gaps, risks, uncertainty, organization-fit observations, and a
   recommendation in validated JSON.
6. Tune thresholds against labeled real jobs and benchmark local models for
   quality, unsupported-claim rate, speed, context size, and memory use.

### Phase D — Application studio

1. Add a dashboard action to prepare an application for a selected job.
2. Build a job-specific evidence plan before drafting prose.
3. Generate an evidence-grounded resume variant, cover letter, short-form answers,
   and a requirements/evidence matrix.
4. Reject drafts containing uncited or unsupported career claims.
5. Store editable source, rendered output, generation metadata, approval state,
   and revisions locally. Never overwrite the canonical career evidence.

### Phase E — Unattended operation

1. Provide one idempotent pipeline command for collect → evaluate → shortlist →
   analyze, with AI-disabled and collection-only modes.
2. Install and remove a Windows Scheduled Task safely; record durable run logs.
3. Add retry/backoff, provider-offline behavior, database/document backup, and a
   local status summary.
4. Add optional notifications only after the local pipeline is reliable.
5. Improve Utah-local discovery based on measured source yield.

## Release gates

| Gate | Required evidence |
|---|---|
| Candidate contract ready | Approved fit spec is versioned, diffable, exportable, and produces the same hard-rule results after reload |
| Local AI ready | Ollama and deterministic adapters pass identical schema-contract tests; collection still passes with Ollama stopped |
| Matching ready | Fixed labeled set meets agreed precision/leakage targets and every positive claim cites valid evidence IDs |
| Application studio ready | A selected job produces a complete editable package with zero unsupported candidate claims in the test set |
| Automation ready | Repeated scheduled runs are idempotent, recover after provider failure, preserve review history, and create verified backups |

## Deferred until evidence supports them

- Automatic application submission.
- Fine-tuning or training a custom model.
- A cloud database or hosted orchestration requirement.
- Paid job-source APIs or paid AI as core dependencies.
- Expanding sources without measuring unique-job yield and recommendation value.

## Current next build chunk

Use `docs/DEVELOPMENT_SPRINTS.md` as the executable backlog. Begin Sprint 0 on
Patrick's Windows database and Sprint 1 in code. Sprint 2 must not select or tune
an Ollama model until the real-job baseline and contract tests exist.
