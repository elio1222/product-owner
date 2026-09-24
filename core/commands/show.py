from storage.strategy import StorageStrategy
from core.schemas import Issue
from core.tools import format_issue

storage = StorageStrategy.from_config()

def show_issue(id):
    issue = storage.get(Issue, id)
    print(format_issue(issue))
    pass
