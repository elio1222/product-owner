import json

import pytest

from conftest import raw_rows, table_names
from core.schemas import Comment, Dependency, Issue
from storage.adapters.sqlite import SqliteAdapter
from storage.strategy import StorageStrategy


def test_insert_and_get_issue(storage, issue):
    storage.insert(issue)
    assert storage.get(Issue, issue.hash_id) == issue


def test_get_missing_returns_none(storage):
    assert storage.get(Issue, "nope") is None


def test_update_issue(storage, issue):
    storage.insert(issue)
    issue.title = "renamed"
    storage.update(issue)
    assert storage.get(Issue, issue.hash_id).title == "renamed"


def test_delete_issue(storage, adapter, issue):
    storage.insert(issue)
    storage.delete(issue)
    assert raw_rows(adapter, "SELECT * FROM issues") == []


def test_insert_and_delete_comment(storage, adapter, issue):
    storage.insert(issue)
    comment = Comment(id=1, issue_id=issue.hash_id, body="hello", author=None)
    storage.insert(comment)
    assert raw_rows(adapter, "SELECT body FROM comments") == [("hello",)]
    storage.delete(comment)
    assert raw_rows(adapter, "SELECT * FROM comments") == []


def test_insert_dependency(storage, adapter, issue):
    other = Issue(title="second")
    storage.insert(issue)
    storage.insert(other)
    storage.insert(Dependency(from_id=issue.hash_id, to_id=other.hash_id))
    assert len(raw_rows(adapter, "SELECT * FROM dependencies")) == 1


def test_overwrite_db_clears_data(storage, adapter, issue):
    storage.insert(issue)
    storage.overwrite_db()
    assert raw_rows(adapter, "SELECT * FROM issues") == []


def test_in_memory_creates_tables():
    s = StorageStrategy.in_memory()
    assert {"issues", "dependencies", "comments", "events"} <= table_names(s.backend)


def _write_config(root, backend):
    po = root / ".po"
    po.mkdir()
    config = {"backend": backend, "database_path": str(po / "database.sqlite")}
    (po / "config.json").write_text(json.dumps(config))


def test_from_config_builds_sqlite_adapter(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, "sqlite")
    assert isinstance(StorageStrategy.from_config().backend, SqliteAdapter)


def test_from_config_unknown_backend_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_config(tmp_path, "mongo")
    with pytest.raises(ValueError):
        StorageStrategy.from_config()
