"""SQLite centraliza os dados. Cada alteração é uma transação exclusiva."""
from contextlib import contextmanager
import json
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS tournament (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS organizer (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    username TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS login_attempt (
    address TEXT PRIMARY KEY,
    failures INTEGER NOT NULL,
    started REAL NOT NULL
);
"""


def connect(path):
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def initialize(path):
    db = connect(path)
    try:
        db.executescript(SCHEMA)
        db.commit()
    finally:
        db.close()


def read(db):
    row = db.execute("SELECT data FROM tournament WHERE id = 1").fetchone()
    return json.loads(row["data"]) if row else None


def save(db, state):
    db.execute("INSERT INTO tournament (id, data) VALUES (1, ?) "
               "ON CONFLICT(id) DO UPDATE SET data = excluded.data",
               (json.dumps(state, ensure_ascii=False),))


@contextmanager
def transaction(path):
    db = connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

