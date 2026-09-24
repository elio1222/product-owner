from typing import Protocol

class AdapterProtocol(Protocol):

    def insert_record(self, table: str, data: dict) -> None:
        """insert a raw record into the given table"""
        ...

    def get_record(self, table: str, id: str, key: str = "hash_id") -> dict | None:
        """fetch the first raw record from the given table where column `key` equals id
        (`key` defaults to the primary key, but can be any column, e.g. "title")"""
        ...

    def get_all_records(self, table: str, filters: dict, math_all: bool) -> list[dict] | None:
        """fetch every raw record from the given table matching `filters` (column -> value);
        math_all=True requires all filters to match (AND), False requires any (OR).
        returns None when nothing matches"""
        ...

    def update_record(self, table: str, id: str, data: dict, key: str = "hash_id") -> None:
        """update a raw record in the given table, matching `key` (the primary key column) to id"""
        ...

    def delete_record(self, table: str, id: str, key: str = "hash_id") -> None:
        """delete a raw record from the given table, matching `key` (the primary key column) to id"""
        ...

    def initialize_db(self) -> None:
        """create default tables for this backend"""
        ...

    def drop_db(self) -> None:
        """drop all tables/collections for this backend"""
        ...
