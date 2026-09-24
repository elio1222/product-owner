from core.schemas import Issue
from core.tools import format_log
from storage.strategy import StorageStrategy

storage = StorageStrategy.from_config()

def get_log(id: str | None = None, limit: int | None = None) -> None:
    if id is not None:
        record = storage.get(Issue, id)
        if record is None:
            raise ValueError(f"an issue with id '{id}' does not exist")
        records = [record]
    else:
        records = storage.filter_all_issues(Issue, None) or []

    # the log is rebuilt from each issue's timestamps and comments
    entries = []
    for r in records:
        issue_id = r["hash_id"]
        entries.append((r["created_at"], issue_id, "created", r["title"]))
        if r["updated_at"]:
            entries.append((r["updated_at"], issue_id, "updated", f"status: {r['status']}"))
        if r["closed_at"]:
            entries.append((r["closed_at"], issue_id, "closed", ""))
        for c in storage.get_comments(issue_id):
            entries.append((c["created_at"], issue_id, "commented", f"{c['author']}: {c['body']}"))

    entries.sort(key=lambda e: str(e[0]))
    if limit is not None:
        entries = entries[-limit:] if limit > 0 else []

    print(format_log(entries))
