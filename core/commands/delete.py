from core.schemas import Issue
from storage.strategy import StorageStrategy

storage = StorageStrategy.from_config()

def delete_issue(id: str) -> str:
    issue = storage.get(Issue, id)

    if issue is None:
        raise ValueError(f"an issue with id '{id}' does not exist")

    storage.delete(issue)

    return issue.title
