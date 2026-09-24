import sqlite3
import sys
from pathlib import Path

import pytest

# make `core` and `storage` importable no matter where pytest is launched from
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.schemas import Issue
from storage.adapters.sqlite import SqliteAdapter
from storage.strategy import StorageStrategy


@pytest.fixture
def adapter():
    """fresh in-memory adapter with tables created, one per test"""
    a = SqliteAdapter(":memory:")
    a.initialize_db()
    yield a
    a.conn.close()


@pytest.fixture
def storage(adapter):
    return StorageStrategy(adapter)


@pytest.fixture(autouse=True)
def fake_config(monkeypatch):
    """Comment.model_post_init reads .po/config.json; give it an in-memory config instead"""
    monkeypatch.setattr("core.schemas.get_config", lambda: {"author": "tester"})


@pytest.fixture
def issue():
    return Issue(title="first issue", desc="something to do")


def raw_rows(adapter: SqliteAdapter, sql: str, params: tuple = ()) -> list[tuple]:
    """query the connection directly, so adapter tests don't depend on get_record"""
    # rows come back as sqlite3.Row (for dict(row) in get_record); Row != tuple, so convert
    return [tuple(r) for r in adapter.conn.execute(sql, params).fetchall()]


def table_names(adapter: SqliteAdapter) -> set[str]:
    rows = raw_rows(adapter, "SELECT name FROM sqlite_master WHERE type = 'table'")
    return {r[0] for r in rows}
