from storage.strategy import StorageStrategy
from core.schemas import Issue
from datetime import datetime

storage = StorageStrategy.from_config()

def update_issue(
    id: str,
    claim: bool = False,
    status: str | None = None,
    title: str | None = None,
    desc: str | None = None,
    type: str | None = None,
):
    record = storage.get(Issue, id)
    if record is None:
        raise ValueError(f"an issue with id '{id}' does not exist")

    # storage.get hands back a raw row, so rebuild the model from it
    issue = Issue(**record)

    if claim:
        issue.status = "in_progress"
    if status is not None:
        issue.status = status
    if title is not None:
        issue.title = title
    if desc is not None:
        issue.desc = desc
    if type is not None:
        issue.type = type

    now = datetime.now()
    if issue.status == "closed":
        issue.closed_at = issue.closed_at or now
    else:
        issue.closed_at = None

    issue.updated_at = now
    storage.update(issue)
