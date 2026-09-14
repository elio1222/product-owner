from core.db import connect_to_db
from pathlib import Path
import subprocess
import json

def get_git_config(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", key],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() or None

def setup_config(author: str | None, email: str | None, desc: str | None, project: str | None) -> Path:

    po_dir = Path(".po")
    po_dir.resolve()
    config_file = f"{po_dir}/config.json"

    if author is None:
        author = get_git_config(key="user.name")
    if email is None:
        email = get_git_config(key="user.email")
    if project is None:
        project = Path.cwd().name

    data = {
        "project": project,
        "author": author,
        "email": email,
        "description": desc
    }

    with open(config_file, "w") as file:
        json.dump(data, file, indent=4)

    return Path(config_file)

def initialize_po(author: str | None, email: str | None, project: str | None, desc: str | None, force: bool, no_git_check: bool) -> bool:

    # if Path(".po").is_dir():
    #     return False
    
    config_path = setup_config(author, email, project, desc)

    conn = connect_to_db()

    return True