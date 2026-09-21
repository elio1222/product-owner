import sqlite3
from pathlib import Path
from typing import Any, Union
from core.schemas import Issue, Dependency, Comment, Event
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

def insert_data_model(conn: sqlite3.Connection, model_type: str, model: Union[Issue, Dependency, Comment, Event]) -> str | Exception:

    insert_queries = {
        "issues": "INSERT INTO issues (hash_id, title, desc, status, type, priority, parent, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        "dependencies": "INSERT INTO dependencies (from_id, to_id, type) VALUES (?, ?, ?)",
        "comments": "INSERT INTO comments (id, issue_id, body, author, created_at) VALUES (?, ?, ?, ?, ?)",
        "events": "INSERT INTO events (id, issue_id, action, payload, created_at) VALUES (?, ?, ?, ?, ?)",
    }

    insert_params = {
        "issues": lambda m: (m["hash_id"], m["title"], m["desc"], m["status"], m["type"], m["priority"], m["parent"], m["created_at"], m["updated_at"]),
        "dependencies": lambda m: (m["from_id"], m["to_id"], m["type"]),
        "comments": lambda m: (m["id"], m["issue_id"], m["body"], m["author"], m["created_at"]),
        "events": lambda m: (m["id"], m["issue_id"], m["action"], m["payload"], m["created_at"]),
    }

    # validating model type before any connection begins
    if model_type not in insert_queries:
        return "invalid model_type"
    
    database_path = get_database_config()
    conn = connect_to_db(database_path)

    # insert specified data model type (issue, comment, event)

    with conn:
        try:
            cur = conn.cursor()
            m = model.model_dump()
            query = insert_queries[model_type]
            params = insert_params[model_type](m)
            cur.execute(query, params)
            return "succesfully inserted values into db"
        except Exception as e:
            return e