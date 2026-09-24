from typing import List, Protocol, Union
from core.schemas import Issue, Dependency, Comment, Event

Model = Union[Issue, Dependency, Comment, Event]

class StorageProtocol(Protocol):

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

    def check_issue_title_exits(self, model: Model) -> bool:
        """check if an issue with this model's title already exists"""
        ...

    def check_issue_parent_exists(self, model: Model) -> bool:
        """check if an issue matching this model's parent already exists"""
        ...

    def get_all_issues(self, model: Model, status: str, type: str) -> List[dict] | None:
        """fetch all issues, filtered by status and type"""
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
