from core.schemas import Issue
from datetime import datetime
from typing import List
import hashlib
from core.db import connect_to_db

def create_issue(title: str, type: str, priority: int, desc: str | None, parent: str | None) -> int:

    # main logic for create subcommand

    # duplicate title warning

    

    # validate parent exists

    issue = Issue(
        title=title,
        type=type,
        priority=priority,
        desc=desc,
        parent=parent
    )

    # insert issue into sql

    return issue.hash_id
    


