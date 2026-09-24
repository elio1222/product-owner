from datetime import datetime
from storage.strategy import StorageStrategy
from core.schemas import Issue

storage = StorageStrategy.from_config()

def close_issue(id: str):
    record = storage.get(Issue, id)
    if record is None:
        raise ValueError(f"an issue with id '{id}' does not exist")

    issue = Issue(**record)
    if issue.status == "closed":
        raise ValueError(f"issue '{id}' is already closed")

    now = datetime.now()
    issue.status = "closed"
    issue.closed_at = now
    issue.updated_at = now
    storage.update(issue)
