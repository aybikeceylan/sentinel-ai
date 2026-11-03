
import sqlite3
import threading
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS incidents (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS metrics (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    data TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS investigations (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    data TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_logs_incident ON logs (incident_id);
CREATE INDEX IF NOT EXISTS idx_metrics_incident ON metrics (incident_id);
CREATE INDEX IF NOT EXISTS idx_investigations_incident
    ON investigations (incident_id);
"""


class Database:
    """A single shared SQLite connection, serialized with a lock."""

    def __init__(self, path: str):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()

        with self._lock:
            self._connection.executescript(SCHEMA)

    def execute(
        self,
        sql: str,
        params: tuple = (),
    ) -> list[tuple]:

        with self._lock:
            rows = self._connection.execute(sql, params).fetchall()
            self._connection.commit()

        return rows

    def execute_many(
        self,
        sql: str,
        rows: list[tuple],
    ) -> None:

        with self._lock:
            self._connection.executemany(sql, rows)
            self._connection.commit()
