# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN PO INTEGRATION v:1 profile:minimal -->
## po Issue Tracker

This project uses **po (product-owner)** for issue tracking. It's a local-first, dependency-aware CLI backed by a SQLite database at `.po/db.sqlite`. Run `po log` for recent activity, or `po list` to see current work.

### Quick Reference

```bash
po create "issue1"            # Create an issue
po show <id>                  # View issue details, dependencies, comments
po ready <id>                 # Find available work — status is open
po update <id>                # Update status of issue - status → in_progress    
po close <id>                 # Complete work — status → closed
po dep <from-id> <to-id>      # Declare that from-id blocks to-id
po comment <id> --body "..."  # Leave a note on an issue
```

### Additional References

If you need a deeper nose dive into `po`, take a look ath `cli_reference.md`, this is the documenation of the whole program to show how you can use these subcommands when you are tracking issues. 

### Rules

- Use `po` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists.
- Use `po comment <id> --body` to leave durable, issue-scoped notes — do NOT use MEMORY.md files.
- Check `po list --blocked` before starting work to confirm nothing is blocking the issue you intend to pick up.

**Architecture in one line:** issues live in a single local SQLite database at `.po/database.sqlite`; there is no sync layer and no multi-machine coordination — everything is scoped to this one checkout. See `README.md` for the full data model and command reference.

## Agent Context Profiles

The managed po block is task-tracking guidance, not permission to override repository, user, or orchestrator instructions.

- **Conservative (default)**: Use `po` for task tracking. Do not run git commits or git pushes unless explicitly asked. At handoff, report changed files, validation, and suggested next commands.
- **Minimal**: Keep tool instruction files as pointers to `README.md`; use the same conservative git policy unless active instructions say otherwise.
- **Team-maintainer**: Only when the repository explicitly opts in, agents may close issues, run quality gates, commit, and push as part of session close. A current "do not commit" or "do not push" instruction still wins.

## Session Completion

This protocol applies when ending a po-tracked implementation workflow. It is subordinate to explicit user, repository, and orchestrator instructions.

1. **File issues for remaining work** — `po create --title "..." --type "task"` for anything that needs follow-up.
2. **Run quality gates** (if code changed) — tests, linters, builds.
3. **Update issue status** — `po close <id>` on finished work, `po comment <id>` to note progress on anything still open.
4. **Handle git by active profile**:
   ```bash
   # Conservative/minimal/default: report status and proposed commands; wait for approval.
   git status

   # Team-maintainer opt-in only, unless current instructions forbid it:
   git pull --rebase
   git push
   git status
   ```
5. **Hand off** — Summarize changes, validation, issue status (`po list --status open`), and any blocked commit/push step.

**Critical rules:**
- Explicit user or orchestrator instructions override this po block.
- Do not commit or push without clear authority from the active profile or the current user request.
- If a required push is blocked, stop and report the exact command and error.
<!-- END PO INTEGRATION -->


## Build & Test

```bash
pip install -e .         # once, inside the venv: installs the `po` command
po init                  # create .po/config.json and .po/database.sqlite
po <command> ...         # run any subcommand, e.g. `po list --status open`
python -m pytest         # run test suite
```

## Architecture Overview

`po` is a local-first, dependency-aware issue tracker backed by SQLite. Structure:

- `main.py` — entry point; registers all subcommands via argparse subparsers.
- `cli/` — one module per positional argument (`create.py`, `list.py`, `show.py`, `update.py`, `ready.py`, `close.py`, `block.py`, `comment.py`, `log.py`). Each exports `register(subparsers)` and parses args / formats output only.
- `core/` — business logic, no argparse. `db.py` (connection + migrations), `models.py` (dataclasses/Pydantic models: Issue, Dependency, Comment, Event), `queries.py` (reusable SQL helpers).
- `.po/` — created at runtime by `po init`; holds `db.sqlite` and `config.json`.

Four tables: `issues`, `dependencies`, `comments`, `events`. Every issue is a node; every dependency is a typed edge (`blocks`, `parent`, `related`). The dependency graph is the source of truth for what's blocked and why.

## Conventions & Patterns

- CLI modules (`cli/*.py`) never contain business logic — they call into `core/` and print/format output.
- `core/` functions never touch argparse or `print()` directly; they return values or raise exceptions, and the CLI layer decides how to present them.
- Issue types (`task`, `bug`, `feature`, `chore`) carry semantic meaning — don't default everything to `task` if a more specific type applies.
- Priority is a sort hint (0 = low … 3 = critical), not a strict queue.
- `--desc` is for real long-form content (acceptance criteria, repro steps, time boxes, ADR reasoning) — if it's more than a sentence, it's doing real work.