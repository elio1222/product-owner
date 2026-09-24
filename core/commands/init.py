from pathlib import Path
import subprocess
import json
from storage.strategy import StorageStrategy

def setup_git() -> None:
    subprocess.run(
        ["git", "init"]
    )

def check_git_status() -> bool:
    result = subprocess.run(
        ["git", "status"],
        capture_output=True,
        text=True
    )

    # checking exit code would be faster and more reliable
    if "fault" in result.stdout:
        return False

    return True

def get_git_config(key: str) -> str | None:
    result = subprocess.run(
        ["git", "config", key],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() or None

def setup_config(*, project: str | None, author: str | None, email: str | None, desc: str, backend: str | None) -> Path:

    po_dir = Path(".po")
    DB_PATH = Path(".po/database.sqlite")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

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
        "description": desc,
        "backend": backend,
        "database_path": str(DB_PATH)
    }

    with open(config_file, "w") as file:
        json.dump(data, file, indent=4)

    return Path(config_file)

def initialize_po(project: str | None, author: str | None, email: str | None, desc: str | None, backend: str, force: bool, no_git_check: bool) -> None:

    config_path = setup_config(project=project, author=author, email=email, desc=desc, backend=backend)

    storage = StorageStrategy.from_config(config_path=config_path)

    # force re runs po init, overwriting everything
    if force:
        storage.overwrite_db()

    # po is already initialized, this is commented out for development purposes
    # if Path(".po").is_dir() and not force:
    #     return

    # git related stuff
    if not no_git_check and not check_git_status():
        initialize_git = input("initialize git for this repo? (Y/N): ").strip().lower()
        while initialize_git != "y" and initialize_git != "n":
            print("invalid choice. try again")
            initialize_git = input("initialize git for this repo? (Y/N): ").strip().lower()
        if initialize_git == "y":
            setup_git()
        elif initialize_git == "n":
            # no git -- project will continue with .po/ initialized
            pass

    

     # will drop all tables for initilization testing purposes
    storage.overwrite_db()