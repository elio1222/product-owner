import sqlite3
from pathlib import Path

DB_PATH = Path(".po/database.sqlite")


def connect_to_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn