from pathlib import Path
from core.schemas import Issue, Dependency, Comment, Event
import json
from storage.protocol import Model
from storage.adapters.protocol import AdapterProtocol
from storage.adapters.sqlite import SqliteAdapter
from typing import Tuple, List

class StorageStrategy:
    """the one chef: business logic lives here, raw backend work is delegated to self.backend"""

    _table_map = {
        Issue: "issues",
        Dependency: "dependencies",
        Comment: "comments",
        Event: "events",
    }

    # primary key column per model. Dependency is deliberately absent: it has a
    # composite key and is only ever inserted (never updated/deleted by id).
    _pk_map = {
        Issue: "hash_id",
        Comment: "id",
        Event: "id",
    }

    @classmethod
    def _pk(cls, model_type: type) -> str:
        try:
            return cls._pk_map[model_type]
        except KeyError:
            raise NotImplementedError(f"{model_type.__name__} has no single-column primary key")

    def __init__(self, backend: AdapterProtocol):
        self.backend = backend

    @classmethod
    def from_config(cls, config_path: Path | None = None) -> "StorageStrategy":
        # config.json only ever stores strings, so translating "backend": "sqlite"
        # into an actual SqliteAdapter has to happen somewhere, exactly once, here.


        def get_configruations(config_path: Path | None = None) -> Tuple[str, Path]:

            if config_path:
                with open(config_file, "r") as file:
                    config = json.load(file)

                return config["backend"], config["database_path"]
            
            po_dir = Path(".po")
            config_file = f"{po_dir}/config.json"

            with open(config_file, "r") as file:
                config = json.load(file)

            return config["backend"], config["database_path"]
            
        backend_name, db_path = get_configruations(config_path=config_path)

        if not backend_name: # checks if backend name is None
            backend_name = "sqlite"

        if backend_name == "sqlite":
            backend = SqliteAdapter(database_path=db_path)
        else:
            raise ValueError(f"unknown backend in config: {backend_name}")

        return cls(backend)

    @classmethod
    def in_memory(cls) -> "StorageStrategy":
        backend = SqliteAdapter(":memory:")
        backend.initialize_db()
        return cls(backend)

    def create_tables(self) -> None:
        self.backend.initialize_db()

    def initialize_backend(self) -> None:
        self.create_tables()

    def _drop_db(self) -> None:
        self.backend.drop_db()

    def overwrite_db(self) -> None:
        self._drop_db()
        self.initialize_backend()

    def check_issue_title_exists(self, model: Model) -> bool:
        m = model.model_dump()
        table = self._table_map[type(model)]

        record = self.backend.get_record(table, id=m["title"], key="title")
        if record:
            return True

        return False

    def check_issue_parent_exists(self, model: Model) -> bool:
        m = model.model_dump()
        table = self._table_map[type(model)]
        record = self.backend.get_record(table, id=m["parent"], key="parent")
        if record:
            return True
        return False

    def filter_all_issues(self, model: Model, status: str | None, type: str | None = None) -> List[dict] | None:
        table = self._table_map[model]
        filters = {
            "status": status,
            "type": type
        }
        if status and type:
            match_all = True
        else:
            match_all = False
        records = self.backend.get_all_records(table, filters, match_all)
        return records
    def insert(self, model: Model) -> None:
        table = self._table_map[type(model)]
        self.backend.insert_record(table, model.model_dump())

    def update(self, model: Model) -> None:
        table = self._table_map[type(model)]
        key = self._pk(type(model))
        self.backend.update_record(table, getattr(model, key), model.model_dump(), key)

    def delete(self, model: Model) -> None:
        table = self._table_map[type(model)]
        key = self._pk(type(model))
        self.backend.delete_record(table, getattr(model, key), key)

    def get(self, model_type: type[Model], id: str) -> Model | None:
        table = self._table_map[model_type]
        raw = self.backend.get_record(table, id, self._pk(model_type))
        return model_type(**raw) if raw else None
