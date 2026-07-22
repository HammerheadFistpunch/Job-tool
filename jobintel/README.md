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

The current ranking implementation is still experimental. Do not treat its
score as a reliable fit judgment until structured profile facets, hard filters,
and labeled evaluation are implemented.

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

See `BUILD_ROADMAP.md` for the revised implementation sequence.
