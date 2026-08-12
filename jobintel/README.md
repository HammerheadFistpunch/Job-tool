# JobIntel

JobIntel is a local-first job collection and matching system. It collects full
job records from public applicant-tracking-system feeds, preserves them in
SQLite, and ranks them against a local career profile. The long-term design uses
Ollama only for detailed analysis of a small shortlist; routine collection and
deduplication do not require an LLM.

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

The structured profile and first deterministic eligibility layer are now in
place. Hard rejections run before semantic ranking and cannot be overridden by
an embedding score. Semantic ranking remains experimental until it is tuned
against Patrick's labeled review decisions.

The prepopulated profile is stored at
`data/input/Profiles/patrick_profile.json`. Known facts and rules are active;
unresolved choices are listed explicitly in `unresolved_decisions`. Missing
salary, unclear locations, and other ambiguous eligibility data produce
`needs_review` rather than automatic rejection.

## Project reference documents

- [`docs/JOB_TOOL_DATA_INTAKE.md`](docs/JOB_TOOL_DATA_INTAKE.md): fill-in
  worksheet for eligibility rules, ranking preferences, resume evidence, and
  job-posting inputs.
- [`docs/JOB_TOOL_FUNCTION_MAP.md`](docs/JOB_TOOL_FUNCTION_MAP.md): current
  components, data flow, Mermaid diagrams, and planned end-state architecture.
- [`BUILD_ROADMAP.md`](BUILD_ROADMAP.md): completed work and implementation
  sequence.

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
- Jobs are not yet marked inactive when they disappear from a source. That will
  be added with source-scoped expiration so an outage cannot falsely expire an
  entire database.

See [`BUILD_ROADMAP.md`](BUILD_ROADMAP.md) for the revised implementation
sequence and [`docs/PROFILE_REVIEW.md`](docs/PROFILE_REVIEW.md) for the short
list of profile choices that still need Patrick's review.
