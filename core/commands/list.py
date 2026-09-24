from storage.strategy import StorageStrategy
from typing import TYPE_CHECKING
from core.schemas import Issue
from core.tools import format_issues

if TYPE_CHECKING:
    from core.schemas import Issue

storage = StorageStrategy.from_config()

def list_issues(status=str | None, type=str | None, priority=int | None):
    issues = storage.filter_all_issues(Issue, status, type, priority)
    # closed issues stay in the table but are hidden unless asked for with --status closed
    if status is None and issues:
        issues = [i for i in issues if i["status"] != "closed"] or None
    print(format_issues(issues))
