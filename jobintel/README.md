# JobIntel

JobIntel is a local-first, agent-independent job intelligence and application
preparation system. It converts career evidence, requirements, preferences, and
organization-fit signals into an approved Job Fit Specification; hunts for
suitable jobs; explains fit with traceable evidence; and prepares application
drafts for selected jobs.

The durable product is the local application, SQLite data, schemas, files, and
CLI—not ChatGPT or any particular model. Collection, hard-rule screening, review,
scheduling, and export are designed to work without AI. Intelligent analysis and
drafting use replaceable providers; Ollama is the first planned live provider,
while hosted services remain optional.

## Current status

The reliable collection foundation is complete:

- Greenhouse collection requests full descriptions with `content=true`.
- Lever JSON feeds are supported.
- Canonical job URLs, source IDs, dates, locations, and raw source records are
  preserved.
- Failed sources are retried and recorded instead of silently returning zero
  jobs.
- SQLite storage deduplicates on source plus source job ID.
- Changed postings update in place; unchanged postings only refresh `last_seen`.
- Every collection run records counts, status, and source errors.
- The legacy database is upgraded in place without deleting existing rows.
- Collection can run independently of sentence-transformers and Ollama.
- Query-driven Jobicy discovery searches across employers without an API key.
- Cross-provider attribution and deduplication preserve one stable review record.
- Per-query remote-US and Utah-area health/count reporting is stored locally.

The structured profile and first deterministic eligibility layer are now in
place. Hard rejections run before semantic ranking and cannot be overridden by
an embedding or model score. Semantic ranking remains experimental until it is
tuned against Patrick's labeled review decisions.

The authoritative prepopulated profile is stored at
`data/input/Profiles/patrick_profile.json`. Known facts and rules are active;
all six initial policy choices are resolved in profile version `2026-08-12.2`.
Missing salary is provisionally eligible; unclear locations and ambiguous
contract or credential requirements produce `needs_review` rather than guesses.
The Markdown `pr_profile.md` remains a human narrative and legacy embedding
input; it is not the source of hard search policy.

## Project reference documents

- [`../READ_FIRST.md`](../READ_FIRST.md): authoritative restart checkpoint,
  verified status, known limitations, and immediate next milestone.
- [`docs/JOB_TOOL_DATA_INTAKE.md`](docs/JOB_TOOL_DATA_INTAKE.md): fill-in
  worksheet for eligibility rules, ranking preferences, resume evidence, and
  job-posting inputs.
- [`docs/JOB_TOOL_FUNCTION_MAP.md`](docs/JOB_TOOL_FUNCTION_MAP.md): current
  components, data flow, Mermaid diagrams, and planned end-state architecture.
- [`BUILD_ROADMAP.md`](BUILD_ROADMAP.md): completed work and implementation
  sequence.
- [`docs/DEVELOPMENT_SPRINTS.md`](docs/DEVELOPMENT_SPRINTS.md): executable sprint
  backlog, dependencies, acceptance criteria, and next tickets.

## Design guarantees

- Local SQLite/files remain the system of record.
- Hard eligibility works with AI disabled and cannot be overridden by AI.
- AI tasks use validated JSON contracts and configurable providers.
- Candidate claims in analysis or application drafts must cite stored evidence.
- Invalid model output is rejected rather than silently accepted.
- Patrick approves fit-spec versions and application packages.
- Automatic application submission is not currently in scope.

## Setup

From the `jobintel` directory:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Edit `config/job_sources.json` to add ATS board tokens. Supported source types
are `greenhouse` and `lever`. A source can be retained but skipped by setting
`"enabled": false`.

The same file contains `discovery_sources`. Jobicy queries are enabled by
default for the target role families. Jobicy is remote-focused; the Utah query
is intentionally reported even when it returns zero local matches.

The default registry now includes 20 companies rather than the original three.
Fourteen boards were live-verified on August 12, 2026; six retained candidate
employers are disabled because their former or guessed ATS token returned 404.
The collector applies the configured role and location prefilter before storage,
records fetched/kept/filtered/error counts per board, and expires a posting only
after its own board completes successfully. Open the **Sources** panel in the
dashboard to inspect board health or enable and disable sources without editing
JSON. Disabled source changes take effect on the next collection run.

Runtime settings live in `config/settings.json`. The dashboard port, collection
schedule, embedding model, and future provider/Ollama configuration are
centralized there. Environment variables such as `JOBINTEL_PORT`,
`JOBINTEL_EMBEDDING_MODEL`, and `JOBINTEL_OLLAMA_MODEL` override the file.

## Commands

Collect and store jobs without loading AI models:

```powershell
python -m backend.collect_jobs
```

Collect, embed, and print recommendations:

```powershell
python -m backend.run_recommendations
```

Evaluate all stored jobs without loading embedding or Ollama models:

```powershell
python -m backend.evaluate_jobs
```

Results are stored in `job_eligibility_evaluations` with the profile version,
decision, exact reasons, and evaluation time. Ineligible jobs remain in the
database for audit but are excluded from semantic ranking.

Start the local review queue:

```powershell
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`. The queue provides job links, eligibility
explanations, posting text, filters, review states, match labels, consistent
interest/rejection reasons, and notes. Review data remains in local SQLite.

Run dependency-light unit tests:

```powershell
python -m unittest discover -s tests -v
```

Validate the reproducible policy fixture:

```powershell
python -m backend.evaluate_fixture
```

Generate a target-machine readiness report:

```powershell
python -m backend.diagnostics
```

The report is saved as `jobintel-readiness.json` and covers Python, packages,
database integrity, profile state, configuration, Ollama reachability, and
installed Ollama models. An unavailable Ollama service is reported without
preventing collection, eligibility, or review work.

Validate the broad-discovery baseline after collection:

```powershell
python -m backend.discovery_report
```

This checks employer count and concentration, reviewable volume, query status,
and explicit remote-US/Utah reporting. The review queue limits only excess
unreviewed reviewable jobs from one employer (10 by default in
`config/settings.json`); it never deletes jobs or hides already-reviewed work.

## Windows launchers

- `Install-JobIntel.cmd` creates `.venv`, installs dependencies, and runs
  diagnostics. It deliberately does not register a Scheduled Task yet.
- `Open-JobIntel.cmd` starts the dashboard minimized and opens it in the default
  browser.
- `Run-Diagnostics.cmd` regenerates the readiness report.

By default, data is stored in `jobintel.db`. Set `JOBINTEL_DB_PATH` to use a
different SQLite file.

## Scheduling on Windows

Use Windows Task Scheduler to run this command from the `jobintel` directory:

```powershell
C:\path\to\Job-tool\jobintel\.venv\Scripts\python.exe -m backend.collect_jobs
```

Start with one collection each morning. Scheduling can be formalized with a
setup script after source selection and expiration behavior are finalized.

## Important data behavior

- Existing review status is not overwritten when a posting changes.
- A partial source failure does not delete jobs from successful earlier runs.
- Jobs missing from a successfully fetched board are marked inactive. A failed
  board never expires its jobs.

## Current collection status

An isolated live run on August 13, 2026 passed the discovery criteria with 107
active jobs across 35 employers and 56 visible reviewable jobs. A consecutive
run created no duplicates and preserved review history. The next target-machine
step is to run collection and `backend.discovery_report` against Patrick's
persistent database, then label approximately 20–30 jobs before matching work.

The next coding work is Sprint 1: add stable career-evidence IDs and a versioned,
user-approved Job Fit Specification. The provider gateway and Ollama adapter
follow in Sprint 2; job understanding and fit analysis follow only after the
baseline and durable schemas exist.

See [`BUILD_ROADMAP.md`](BUILD_ROADMAP.md) for the revised implementation
sequence and [`docs/PROFILE_REVIEW.md`](docs/PROFILE_REVIEW.md) for the resolved
profile policy.
