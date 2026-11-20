import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    company      TEXT NOT NULL,
    position     TEXT NOT NULL,
    location     TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL,
    applied_date TEXT,
    notes        TEXT NOT NULL DEFAULT ''
);
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn
