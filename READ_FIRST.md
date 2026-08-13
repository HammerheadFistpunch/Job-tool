# READ FIRST — JobIntel Development Handoff

This is the authoritative pickup point for the next development session. Read
this file, then `jobintel/BUILD_ROADMAP.md` and
`jobintel/docs/DEVELOPMENT_SPRINTS.md` before changing code.

## Product mission

JobIntel is a local-first, agent-independent job intelligence and application
preparation system. It must:

1. Turn Patrick's work history, requirements, preferences, and organization-fit
   signals into a versioned, user-approved Job Fit Specification.
2. Search repeatedly for suitable remote-US and Sandy/Salt Lake-area jobs.
3. Apply deterministic eligibility rules before any model scoring.
4. Use replaceable AI providers to understand postings and compare requirements
   with stored career evidence.
5. Prepare evidence-grounded application documents for jobs Patrick selects.
6. Keep collection, storage, review, scheduling, and document history useful
   without ChatGPT Premium or any paid model.

## Non-negotiable architecture

- The application, data, prompts, schemas, CLI commands, and workflow state live
  in this repository and local SQLite/files—not in a particular chat or agent.
- Collection, normalization, deduplication, deterministic eligibility, review,
  scheduling, and export must work with AI disabled.
- AI features use provider-neutral structured contracts. Ollama is the first
  supported runtime; hosted providers are optional adapters, never dependencies.
- A hard eligibility failure cannot be overridden by embeddings or an LLM.
- Model output is untrusted until schema validation succeeds. Unsupported career
  claims must be rejected unless they cite stored evidence IDs.
- Missing or ambiguous eligibility data normally produces `needs_review`, not a
  guessed rejection.
- Application documents are drafts requiring Patrick's approval. Automatic
  application submission is outside the current roadmap.
- Schema migrations must preserve jobs, source provenance, reviews, analyses,
  applications, and Patrick's feedback.

## Verified repository state

- Repository: `HammerheadFistpunch/Job-tool`
- Authoritative integration branch: `GPT_Redesign`
- Verified remote baseline: `f6135a82134321c1842251be49a9cfaf23b7a4bc`
- Local application folder: `jobintel`
- Candidate profile version: `2026-08-12.2`
- Target platform: Windows 11, Python 3.12.8, local SQLite, local Ollama

Always fetch `origin/GPT_Redesign` before implementation and treat the remote
branch as authoritative. Do not assume the baseline SHA is still current.

## What works now

- Query-based Jobicy discovery plus configured Greenhouse and Lever boards.
- Complete normalized postings, canonical links, source/query attribution,
  cross-provider deduplication, change detection, and safe expiration.
- SQLite persistence and collection/source health history.
- Versioned structured profile and explainable deterministic eligibility.
- Local FastAPI review queue with states, labels, reasons, notes, and evidence.
- Review metrics, policy fixture, diagnostics, and Windows launchers.
- A diversity-capped queue that does not delete jobs or hide reviewed records.
- Latest isolated validation: 51 passing tests; 107 active jobs across 35
  employers; 56 visible reviewable jobs across 29 employers; largest employer
  share 17.86%; a second run created no duplicates and preserved review state.

## Important gaps

- The current profile is structured but is not yet a generated, reviewable Job
  Fit Specification with stable provenance.
- Career achievements do not yet have stable evidence IDs suitable for citation.
- Facet retrieval, long-description chunking, requirement extraction, and
  evidence-grounded fit analysis are not built.
- There is no provider-neutral model gateway or working Ollama analysis path.
- Personality and preferred organization traits are stored but not assessed.
- Application package generation and application document history are not built.
- Background scheduling, durable run logs, backups, and failure notification are
  not installed.
- The no-key broad source remains remote-focused and produced no Utah-local jobs
  in the last validation.

## Immediate next milestone

Establish the evaluation baseline before tuning matching:

1. Run collection and the discovery report against Patrick's persistent Windows
   database.
2. Label approximately 20–30 jobs from the diverse queue.
3. Record precision at 10, hard-reject leakage, coverage, and reason frequency.
4. Freeze those labels as the initial real-job regression dataset.

In parallel with user labeling, Sprint 1 may begin on evidence IDs, the Job Fit
Specification schema, and migration-safe storage because those changes do not
depend on score tuning.

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

Then inspect:

- `jobintel/BUILD_ROADMAP.md`
- `jobintel/docs/DEVELOPMENT_SPRINTS.md`
- `jobintel/docs/JOB_TOOL_FUNCTION_MAP.md`
- `jobintel/data/input/Profiles/patrick_profile.json`
- `jobintel/config/job_sources.json`
- `jobintel/config/settings.json`

## Next user checkpoint

Patrick's next hands-on task is to label 20–30 diverse jobs. The next coding
sprint is Sprint 1, Candidate Intelligence Foundation. Do not tune ranking or
choose a local model based on intuition before the labeled baseline exists.
