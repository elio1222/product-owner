from core.schemas import Issue
from storage.strategy import StorageStrategy

storage = StorageStrategy.from_config()

def block_issues(from_id: str, to_id: str) -> None:
    if from_id == to_id:
        raise ValueError("an issue cannot depend on itself")

    blocker = storage.get(Issue, from_id)
    if blocker is None:
        raise ValueError(f"an issue with id '{from_id}' does not exist")

    blocked = storage.get(Issue, to_id)
    if blocked is None:
        raise ValueError(f"an issue with id '{to_id}' does not exist")

    if storage.dependency_exists(from_id, to_id):
        raise ValueError(f"'{from_id}' already blocks '{to_id}'")

    storage.add_dependency(from_id, to_id)

    # a finished blocker doesn't hold anything back, and a closed issue stays closed
    if blocker.status != "closed" and blocked.status != "closed":
        blocked.status = "blocked"
        storage.update(blocked)
