"""SQLite connection and schema management for JobIntel.

The collector uses the standard-library sqlite3 driver so collection and
deduplication do not depend on the AI stack being installed. SQLAlchemy can
still be used by the future FastAPI layer, but it is not required to run the
database migrations or storage tests.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "jobintel.db"


def database_path() -> Path:
    configured = os.getenv("JOBINTEL_DB_PATH")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_DATABASE_PATH


def connect_database(path: str | Path | None = None) -> sqlite3.Connection:
    resolved = Path(path).resolve() if path else database_path()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(resolved)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


JOB_COLUMNS = {
    "external_id": "TEXT",
    "source": "TEXT",
    "canonical_url": "TEXT",
    "posted_at": "TEXT",
    "updated_at": "TEXT",
    "first_seen_at": "TEXT",
    "last_seen_at": "TEXT",
    "content_hash": "TEXT",
    "active": "INTEGER NOT NULL DEFAULT 1",
    "raw_json": "TEXT",
    "similarity_score": "REAL",
}


def _column_names(connection: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the current schema and non-destructively upgrade the legacy DB."""

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT,
            source TEXT,
            company TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            location TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            canonical_url TEXT,
            source_url TEXT,
            posted_at TEXT,
            updated_at TEXT,
            first_seen_at TEXT,
            last_seen_at TEXT,
            content_hash TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            raw_json TEXT,
            similarity_score REAL,
            status TEXT NOT NULL DEFAULT 'discovered'
        );

        CREATE TABLE IF NOT EXISTS collection_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL DEFAULT 'running',
            fetched_count INTEGER NOT NULL DEFAULT 0,
            new_count INTEGER NOT NULL DEFAULT 0,
            updated_count INTEGER NOT NULL DEFAULT 0,
            unchanged_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0,
            errors_json TEXT NOT NULL DEFAULT '[]'
        );
        """
    )

    # The repository snapshot contains an early jobs table. Add missing fields
    # in place so existing records and user status values survive the upgrade.
    existing = _column_names(connection, "jobs")
    for name, definition in JOB_COLUMNS.items():
        if name not in existing:
            connection.execute(f"ALTER TABLE jobs ADD COLUMN {name} {definition}")

    connection.executescript(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_jobs_source_external_id
            ON jobs(source, external_id)
            WHERE source IS NOT NULL AND external_id IS NOT NULL;
        CREATE INDEX IF NOT EXISTS ix_jobs_active_score
            ON jobs(active, similarity_score DESC);
        CREATE INDEX IF NOT EXISTS ix_jobs_last_seen
            ON jobs(last_seen_at);
        """
    )
    connection.commit()

