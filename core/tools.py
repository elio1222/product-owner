from pathlib import Path
import json
import os
import shutil
import sys
import textwrap

RULE = None  # sentinel row: draws a horizontal divider inside a table

STATUS_LABEL = {"open": "open", "in_progress": "wip", "blocked": "blkd", "closed": "done"}
STATUS_ORDER = {"open": 0, "in_progress": 1, "blocked": 2, "closed": 3}
STATUS_COLOR = {"open": "32", "in_progress": "33", "blocked": "31", "closed": "2"}
PRIORITY_COLOR = {0: "1;31", 1: "31", 2: "33", 3: "0", 4: "2"}

def get_config() -> dict:
    config_path = Path(".po/config.json")

    with open(config_path, "r") as file:
        config = json.load(file)

    return config

def _use_color() -> bool:
    return sys.stdout.isatty() and "NO_COLOR" not in os.environ

def _fmt_time(value) -> str:
    if not value:
        return "-"
    if hasattr(value, "strftime"):
        return value.strftime("%Y-%m-%d %H:%M")
    return str(value)[:16].replace("T", " ")

def _render_table(header, rows, wrap_col: int, max_width: int | None = None) -> str:
    """bordered table. `rows` holds lists of cells (a cell is a str or a (str, ansi_code) pair)
    or RULE for a divider. Every column fits its longest value except `wrap_col`, which takes
    the remaining terminal width and word-wraps onto continuation lines instead of truncating."""
    color = _use_color()
    text = lambda cell: cell[0] if isinstance(cell, tuple) else cell
    body = [r for r in rows if r is not RULE]

    widths = [max(len(text(r[c])) for r in [header, *body]) for c in range(len(header))]
    borders = 3 * len(header) + 1  # "| " + " | " * (n - 1) + " |"
    limit = max_width or shutil.get_terminal_size().columns
    room = max(limit - (sum(widths) - widths[wrap_col]) - borders, 10)
    widths[wrap_col] = min(widths[wrap_col], room)

    def paint(cell, width: int) -> str:
        value, code = cell if isinstance(cell, tuple) else (cell, None)
        padded = value.ljust(width)  # pad the plain text first so escape codes don't skew alignment
        return f"\033[{code}m{padded}\033[0m" if code and color else padded

    def wrap(cell, width: int) -> list:
        value, code = cell if isinstance(cell, tuple) else (cell, None)
        chunks = [
            chunk
            for para in value.splitlines() or [""]
            for chunk in (textwrap.wrap(para, width, break_long_words=True) or [""])
        ]
        return [(chunk, code) for chunk in chunks]

    def line(row) -> list:
        cells = [wrap(row[c], widths[c]) for c in range(len(widths))]
        height = max(len(c) for c in cells)
        return [
            "| " + " | ".join(
                paint(cells[c][i] if i < len(cells[c]) else "", widths[c]) for c in range(len(widths))
            ) + " |"
            for i in range(height)
        ]

    rule = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    out = [rule, *line(header), rule]
    for row in rows:
        out.extend([rule] if row is RULE else line(row))
    out.append(rule)
    return "\n".join(out)

def format_issues(issues: list[dict], blocked_by: dict[str, list[str]] | None = None) -> str:
    """bordered table with one row per issue, triage-ordered (active before closed, then by
    priority, then oldest first). `blocked_by` maps an issue id to the ids holding it back and
    adds a BLOCKED BY column when any issue has blockers."""
    if not issues:
        return "no issues found"

    blocked_by = blocked_by or {}
    ordered = sorted(
        issues,
        key=lambda i: (
            STATUS_ORDER.get(i["status"], len(STATUS_ORDER)),
            i["priority"] if i["priority"] is not None else 99,
            str(i["created_at"]),
        ),
    )

    show_blockers = any(blocked_by.get(i["hash_id"]) for i in ordered)
    header = ["ID", "PRI", "TYPE", "STATUS", "PARENT"] + (["BLOCKED BY"] if show_blockers else []) + ["TITLE"]

    rows = []
    for i in ordered:
        priority = i["priority"]
        row = [
            i["hash_id"],
            (f"P{priority}", PRIORITY_COLOR.get(priority)) if priority is not None else "-",
            i["type"] or "-",
            (STATUS_LABEL.get(i["status"], i["status"]), STATUS_COLOR.get(i["status"])),
            i.get("parent") or "-",
        ]
        if show_blockers:
            row.append(", ".join(blocked_by.get(i["hash_id"], [])) or "-")
        row.append(i["title"])
        rows.append(row)

    open_count = sum(1 for i in ordered if i["status"] != "closed")
    blocked_count = sum(1 for i in ordered if i["status"] == "blocked")
    footer = f"{len(ordered)} issues · {open_count} active · {blocked_count} blocked"

    return _render_table(header, rows, wrap_col=len(header) - 1) + "\n" + footer

def format_issue(issue: dict) -> str:
    """bordered two-column table (field | value) showing everything about one issue;
    long values, like the description, are word-wrapped to fit the terminal"""
    priority = issue.get("priority")
    status = issue["status"]
    rows = [
        ["ID", issue["hash_id"]],
        RULE,
        ["Title", issue["title"]],
        ["Status", (STATUS_LABEL.get(status, status), STATUS_COLOR.get(status))],
        ["Type", issue.get("type") or "-"],
        ["Priority", (f"P{priority}", PRIORITY_COLOR.get(priority)) if priority is not None else "-"],
        ["Parent", issue.get("parent") or "-"],
        ["Created", _fmt_time(issue.get("created_at"))],
        ["Updated", _fmt_time(issue.get("updated_at"))],
        RULE,
        ["Description", issue.get("desc") or "-"],
    ]
    return _render_table(["FIELD", "VALUE"], rows, wrap_col=1, max_width=min(shutil.get_terminal_size().columns, 100))
