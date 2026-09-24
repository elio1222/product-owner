from pathlib import Path
import json
import shutil

def get_config() -> dict:
    config_path = Path(".po/config.json")

    with open(config_path, "r") as file:
        config = json.load(file)

    return config

def format_issues(issues: list["Issue"]) -> str:
    HEADER = ("ID", "PRI", "TYPE", "STATUS", "TITLE")
    """bordered table with one row per issue; the title column shrinks to fit the terminal"""
    if not issues:
        return "no issues found"

    rows = [
        (
            i["hash_id"],
            f"P{i["priority"]}" if i["priority"] is not None else "-",
            i["type"] or "-",
            i["status"],
            i["title"],
        )
        for i in issues
    ]

    # each column is as wide as its longest value, except the title, which is
    # capped so the whole table fits the terminal ("| " + " | " * n + " |" = 3n + 1 chars of borders)
    widths = [max(len(r[c]) for r in [HEADER, *rows]) for c in range(len(HEADER))]
    borders = 3 * len(HEADER) + 1
    title_room = max(shutil.get_terminal_size().columns - sum(widths[:-1]) - borders, 10)
    widths[-1] = min(widths[-1], title_room)

    def cell(text: str, width: int) -> str:
        return (text if len(text) <= width else text[: width - 1] + "…").ljust(width)

    def line(row) -> str:
        return "| " + " | ".join(cell(row[c], widths[c]) for c in range(len(widths))) + " |"

    rule = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    return "\n".join([rule, line(HEADER), rule, *(line(r) for r in rows), rule])