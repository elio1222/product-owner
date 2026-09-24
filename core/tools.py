from pathlib import Path
import json
import shutil
import textwrap

def get_config() -> dict:
    config_path = Path(".po/config.json")

    with open(config_path, "r") as file:
        config = json.load(file)

    return config

def format_issues(issues: list[dict]) -> str:
    """bordered table with one row per issue, most urgent (lowest priority number) first;
    the title column shrinks to fit the terminal"""
    HEADER = ("ID", "PRI", "TYPE", "STATUS", "TITLE")
    if not issues:
        return "no issues found"

    rows = [
        (
            i["hash_id"],
            f"P{i['priority']}" if i["priority"] is not None else "-",
            i["type"] or "-",
            i["status"],
            i["title"],
        )
        for i in sorted(issues, key=lambda i: i["priority"] if i["priority"] is not None else 99)
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

def format_issue(issue: dict, dependents: list[str] | None = None, comments: list[dict] | None = None) -> str:
    """bordered field | value table with the full detail of one issue, split into sections
    (id, fields, dependencies, description, comments). The table is only as wide as its content
    needs, up to the terminal width, and long values are word-wrapped instead of truncated."""
    def when(value) -> str:
        return str(value)[:16].replace("T", " ") if value else "-"

    sections = [
        [("ID", issue["hash_id"])],
        [
            ("Title", issue["title"]),
            ("Status", issue["status"]),
            ("Type", issue["type"] or "-"),
            ("Priority", f"P{issue['priority']}" if issue["priority"] is not None else "-"),
            ("Parent", issue["parent"] or "-"),
            ("Created", when(issue["created_at"])),
            ("Updated", when(issue["updated_at"])),
        ],
        [("Blocks", ", ".join(dependents or []) or "-")],
        [("Description", issue["desc"] or "-")],
        [
            ("Comments" if n == 0 else "", f"{when(c['created_at'])} {c['author']}: {c['body']}")
            for n, c in enumerate(comments)
        ] if comments else [("Comments", "-")],
    ]

    rows = [row for section in sections for row in section]
    key_width = max(len(k) for k, _ in rows)
    # widest single line of any value, capped so the whole table fits the terminal (7 = "| " + " | " + " |")
    longest = max(len(line) for _, v in rows for line in v.splitlines() or [""])
    value_width = max(min(longest, min(shutil.get_terminal_size().columns, 100) - key_width - 7), 20)

    rule = "+" + "-" * (key_width + 2) + "+" + "-" * (value_width + 2) + "+"
    lines = [rule]
    for section in sections:
        for key, value in section:
            # wrap each paragraph separately so line breaks in the description survive
            wrapped = [chunk for para in value.splitlines() or [""] for chunk in (textwrap.wrap(para, value_width) or [""])]
            for n, chunk in enumerate(wrapped):
                lines.append(f"| {(key if n == 0 else '').ljust(key_width)} | {chunk.ljust(value_width)} |")
        lines.append(rule)
    return "\n".join(lines)
