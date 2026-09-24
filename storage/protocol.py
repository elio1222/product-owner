from pathlib import Path
from typing import Protocol, Union
from core.schemas import Issue, Dependency, Comment, Event

Model = Union[Issue, Dependency, Comment, Event]

class StorageProtocol(Protocol):

    def _get_configurations(self) -> Path:
        """get database configuration, used as an internal helper for later methods"""
        ...

    def _connect_to_db(self) -> None:
        """connecting itself to db as an internal helper"""
        ...

    def create_tables(self) -> None:
        """create default tables for program"""
        ...

    def initialize_backend(self) -> None:
        """set up the backend from scratch"""
        ...

    def _drop_db(self) -> None:
        """drop tables, used when overwriting backend"""
        ...

    def overwrite_db(self) -> None:
        """restarting db"""
        ...

    def title_exists(self, title: str) -> bool:
        """check if an issue with this title already exists"""
        ...

    def insert(self, model: Model) -> None:
        """insert model into db, dispatched on the model's own type"""
        ...

    def update(self, model: Model) -> None:
        """update existing row for model, dispatched on the model's own type"""
        ...

    def delete(self, model: Model) -> None:
        """delete row for model, dispatched on the model's own type"""
        ...

    def get(self, model_type: type[Model], id: str) -> Model | None:
        """fetch a row by id, dispatched on model_type since no instance exists yet"""
        ...
