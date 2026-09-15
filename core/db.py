import sqlite3
from pathlib import Path


def drop_all_tables(conn: sqlite3.Connection) -> None:
    with conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("DROP TABLE IF EXISTS comments")
        cur.execute("DROP TABLE IF EXISTS dependencies")
        cur.execute("DROP TABLE IF EXISTS issues")


def connect_to_db(database_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    return conn

def create_default_tables(conn: sqlite3.Connection) -> None:
    """create default tables for sqlite3 and product owner"""
    with conn:
        cur = conn.cursor()
        cur.execute("""
CREATE TABLE IF NOT EXISTS issues (
hash_id TEXT PRIMARY KEY,
title TEXT NOT NULL,
desc TEXT,
status TEXT NOT NULL DEFAULT 'open',
type TEXT NOT NULL DEFAULT 'task',
priority INTEGER,
parent TEXT,
created_at TEXT NOT NULL,
updated_at TEXT,
FOREIGN KEY (parent) REFERENCES issues(hash_id)
)
""")
        cur.execute("""
CREATE TABLE IF NOT EXISTS dependencies (
id INTEGER PRIMARY KEY,
from_id TEXT,
to_id TEXT,
type TEXT NOT NULL DEFAULT 'blocks',
FOREIGN KEY (from_id) REFERENCES issues(hash_id),
FOREIGN KEY (to_id) REFERENCES issues(hash_id)
)
""")
        cur.execute("""
CREATE TABLE IF NOT EXISTS comments (
id INTEGER PRIMARY KEY,
issue_id TEXT,
body TEXT,
author TEXT,
created_at TEXT,
FOREIGN KEY (issue_id) REFERENCES issues(hash_id)
)
""")
        # global log throughout the whole project
        cur.execute("""
CREATE TABLE IF NOT EXISTS events (
id INTEGER PRIMARY KEY,
issue_id TEXT,
action TEXT,
payload TEXT,
created_at TEXT,
FOREIGN KEY (issue_id) REFERENCES issues(hash_id)
)
""")