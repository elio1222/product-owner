import sqlite3

import pytest

from conftest import raw_rows, table_names

ISSUE = {
    "hash_id": "abc123",
    "title": "write tests",
    "desc": None,
    "status": "open",
    "type": "task",
    "priority": 2,
    "parent": None,
    "created_at": "2026-01-01T00:00:00",
    "updated_at": None,
}


def test_initialize_creates_tables(adapter):
    assert {"issues", "dependencies", "comments", "events"} <= table_names(adapter)


def test_drop_db_removes_tables(adapter):
    adapter.drop_db()
    assert not {"issues", "dependencies", "comments", "events"} & table_names(adapter)


def test_insert_and_get(adapter):
    adapter.insert_record("issues", ISSUE)
    assert adapter.get_record("issues", "abc123") == ISSUE


def test_get_missing_returns_none(adapter):
    assert adapter.get_record("issues", "nope") is None


def test_duplicate_id_raises(adapter):
    adapter.insert_record("issues", ISSUE)
    with pytest.raises(sqlite3.IntegrityError):
        adapter.insert_record("issues", ISSUE)


def test_update(adapter):
    adapter.insert_record("issues", ISSUE)
    adapter.update_record("issues", "abc123", {"title": "renamed"})
    assert adapter.get_record("issues", "abc123")["title"] == "renamed"


def test_delete(adapter):
    adapter.insert_record("issues", ISSUE)
    adapter.delete_record("issues", "abc123")
    assert raw_rows(adapter, "SELECT * FROM issues") == []
