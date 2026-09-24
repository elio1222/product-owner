from storage.strategy import StorageStrategy
from typing import TYPE_CHECKING
from core.schemas import Issue
from core.tools import format_issues

if TYPE_CHECKING:
    from core.schemas import Issue

storage = StorageStrategy.from_config()

def list_issues(status=str | None, type=str | None):
    issues = storage.filter_all_issues(Issue, status, type)
    print(format_issues(issues))
