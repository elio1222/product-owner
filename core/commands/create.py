from core.schemas import Issue
from datetime import datetime
from typing import List
import hashlib
from storage.strategy import StorageStrategy

storage = StorageStrategy.from_config()

def create_issue(title: str, type: str, priority: int, desc: str | None, parent: str | None) -> int:

    # main logic for create subcommand
    issue = Issue(
        title=title,
        type=type,
        priority=priority,
        desc=desc,
        parent=parent
    )
    # duplicate title warning
    if storage.check_issue_title_exists(issue):
        raise ValueError(f"an issue with title '{title}' already exists")

    # validate parent exists
    # if storage.check_issue_parent_exists(issue):
    #     pass
    # else:
    #     raise ValueError(f"an issue with {parent} does not exist")
    
    # insert issue into database
    storage.insert(issue)

    # checks again if parents exists to insert into dependency edge tables
    parent = issue.model_dump()["parent"]
    if parent:
        storage.create_dependency_edge(issue)

    return issue.hash_id
    


