from storage.strategy import StorageStrategy
from core.schemas import Issue
from core.tools import format_issue

storage = StorageStrategy.from_config()

def show_issue(id):
    issue = storage.get(Issue, id)
    if issue is None:
        raise ValueError(f"an issue with id '{id}' does not exist")

    print(format_issue(issue, storage.get_dependents(id), storage.get_comments(id)))
