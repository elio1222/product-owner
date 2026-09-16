import sqlite3
from pathlib import Path
from typing import Any
from core.schemas import Issue
import json

def get_database_config() -> Path:
    po_dir = Path(".po")
    config_file = f"{po_dir}/config.json"

    with open(config_file, "r") as file:
        config = json.load(file)

    return Path(config["database_path"])
def drop_all_tables(conn: sqlite3.Connection) -> None:
    with conn:
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS events")
        cur.execute("DROP TABLE IF EXISTS comments")
        cur.execute("DROP TABLE IF EXISTS dependencies")
        cur.execute("DROP TABLE IF EXISTS issues")


def connect_to_db(database_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = 'ON'")
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
priority INTEGER DEFAULT 2,
parent TEXT,
created_at TEXT NOT NULL,
updated_at TEXT,
FOREIGN KEY (parent) REFERENCES issues(hash_id)
)
""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status)")
        cur.execute("""
CREATE TABLE IF NOT EXISTS dependencies (
from_id TEXT NOT NULL REFERENCES issues(hash_id) ON DELETE CASCADE,
to_id TEXT NOT NULL REFERENCES issues(hash_id) ON DELETE CASCADE,
type TEXT NOT NULL DEFAULT 'blocks',
PRIMARY KEY(from_id, to_id, type),
CHECK (from_id != to_id)
)
""")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_to ON dependencies(to_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_dependencies_from ON dependencies(from_id)")
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
        cur.execute("CREATE INDEX IF NOT EXISTS idx_comments_id ON comments(issue_id)")
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

def insert_data_model(conn: sqlite3.Connection, model_type: str, model: Any) -> str:

    database_path = get_database_config()
    cur = connect_to_db(database_path)
    # insert specified data model type (issue, comment, event)

    if isinstance(model, Issue):
        m = model.model_dump()
        query = """"""
        cur.execute(query, ())


    return