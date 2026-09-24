from core.schemas import Issue, Comment
from storage.strategy import StorageStrategy

storage = StorageStrategy.from_config()

def add_comment(id: str, body: str, author: str | None = None) -> None:
    if not body or not body.strip():
        raise ValueError("a comment cannot be empty")

    if storage.get(Issue, id) is None:
        raise ValueError(f"an issue with id '{id}' does not exist")

    # author=None falls back to the author in .po/config.json (see Comment.model_post_init)
    storage.insert(Comment(issue_id=id, body=body.strip(), author=author))
