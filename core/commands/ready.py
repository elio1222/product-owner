from storage.strategy import StorageStrategy
from typing import TYPE_CHECKING
from core.tools import format_issues
from core.schemas import Issue

if TYPE_CHECKING:
    from core.schemas import Issue

storage = StorageStrategy.from_config()

def ready_issue():
    issues = storage.filter_all_issues(Issue, status="open", type=None)
    print(format_issues(issues))
    
