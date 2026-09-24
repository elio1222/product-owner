import sqlite3
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from pathlib import Path

class SqliteAdapter:
    """raw sqlite plumbing only, no business logic"""

    def __init__(self, database_path: Path | str):
        self.conn = sqlite3.connect(database_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = 'ON'")

    def insert_record(self, table: str, data: dict) -> None:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        with self.conn:
            self.conn.execute(
                f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
                tuple(data.values()),
            )

    def get_record(self, table: str, id: str, key: str = "hash_id") -> dict | None:
        row = self.conn.execute(f"SELECT * FROM {table} WHERE {key} = ?", (id,)).fetchone()
        return dict(row) if row else None

    def get_all_records(self, table: str, filters: dict, match_all: bool = True) -> List[dict] | None:
        joiner = " AND " if match_all else " OR "
        where_clause = joiner.join(f"{key} = ?" for key in filters)
        values = tuple(filters.values())
        if not all(x is None for x in values):
            query = f"SELECT * FROM {table} WHERE {where_clause}"
            rows = self.conn.execute(query, values).fetchall()
        else:
            query = f"SELECT * FROM {table}"
            rows = self.conn.execute(query).fetchall()
        result = [dict(row) for row in rows]
        return result if result else None

    def update_record(self, table: str, id: str, data: dict, key: str = "hash_id") -> None:
        assignments = ", ".join(f"{column} = ?" for column in data)
        with self.conn:
            self.conn.execute(
                f"UPDATE {table} SET {assignments} WHERE {key} = ?",
                (*data.values(), id),
            )

    def delete_record(self, table: str, id: str, key: str = "hash_id") -> None:
        with self.conn:
            self.conn.execute(f"DELETE FROM {table} WHERE {key} = ?", (id,))

    def drop_db(self) -> None:
        with self.conn:
            cur = self.conn.cursor()
            cur.execute("DROP TABLE IF EXISTS events")
            cur.execute("DROP TABLE IF EXISTS comments")
            cur.execute("DROP TABLE IF EXISTS dependencies")
            cur.execute("DROP TABLE IF EXISTS issues")

    def initialize_db(self) -> None:
        with self.conn:
            cur = self.conn.cursor()
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
closed_at TEXT,
FOREIGN KEY (parent) REFERENCES issues(hash_id)
)
""")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status)")
            cur.execute("""
CREATE TABLE IF NOT EXISTS dependencies (
from_id TEXT NOT NULL REFERENCES issues(hash_id) ON DELETE CASCADE,
to_id TEXT NOT NULL REFERENCES issues(hash_id) ON DELETE CASCADE,
PRIMARY KEY(from_id, to_id),
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
