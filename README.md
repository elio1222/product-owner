# product-owner

A local-first, dependency-aware issue tracker for personal use and agent-driven task management. Inspired by [beads](https://beads.gascity.com/architecture), simplified for a single engineer or autonomous agent.

---

## What This Is

`po` is a CLI that lets you model work as interconnected issues, track their status, and declare how they block each other. It stores everything in a local SQLite database inside `.po/` at the root of each project. No cloud. No sync. Just a clean dependency graph you can query from the terminal.

---

## Directory Layout

```
product-owner/
├── main.py          # entry point; registers all subcommands via argparse subparsers
├── cli/             # one module per positional argument
│   ├── init.py
│   ├── create.py
│   ├── list.py
│   ├── show.py
│   ├── update.py
│   ├── ready.py
│   ├── close.py
│   ├── block.py
│   ├── comment.py
│   └── log.py
├── core/            # business logic, no argparse here
│   ├── commands/    # cli logic
│   |    ├── *.py    # logic for each subcommand in cli/
│   ├── db.py        # SQLite connection, schema, and all SQL statements
│   ├── schemas.py   # Pydantic Models: Issue, Dependency, Comment, Event
│   └── tools.py     # shared helpers (e.g. reading .po/config.json)
└── .po/             # created at runtime by `po init`
    ├── database.sqlite
    └── config.json
```

---

## Subcommand Contract

Every `cli/*.py` module exports exactly one function: `register(subparsers)`. It adds its subparser and sets `func` on it. `main.py` imports each module and calls `register`. This keeps `main.py` clean and each command self-contained.

```
register(sub)  →  adds parser, sets p.set_defaults(func=handle)
handle(args)   →  calls into core/, prints output, exits
```

Business logic lives in `core/`. CLI modules only parse arguments and format output.

Unit tests will be done in tests/ to validate and ensure integrity for business logic. 

---

## Implementation Status

This README documents the intended contract for every command, not just what's wired up today. Current state:

| Command   | Status                                                                 |
|-----------|-------------------------------------------------------------------------|
| `init`    | Implemented — writes `.po/config.json`, creates tables               |
| `create`  | Partially implemented — builds and validates the `Issue`, but does not yet persist it to the database |
| `list`, `show`, `update`, `ready`, `close`, `block`, `comment`, `log` | Stubbed — `cli/*.py` and `core/commands/*.py` exist and register with `main.py`, but the underlying functions are `pass` (no-ops) |

---

## Commands

| Command   | Arguments / Flags                                                              | Purpose                                               |
|-----------|---------------------------------------------------------------------------------|--------------------------------------------------------|
| `init`    | `--author` `--email` `--project` `--desc` `--force` `--no-git-check`          | Create `.po/config.json` and `.po/database.sqlite`, run schema setup |
| `create`  | `--title` (required) `--type` `--priority` `--desc` `--parent`                | Create a new issue; prints assigned ID                |
| `list`    | `--status` `--type`                                                | Tabular list with optional filters                    |
| `show`    | `<id>`                                                                          | Full issue detail: fields, dependencies, comments      |
| `update`  | `<id>` `--status`                                                               | Patch an existing issue's status                       |
| `ready`   | `<id>`                                                                          | Shortcut: status → `in_progress`                       |
| `close`   | `<id>`                                                                          | Shortcut: status → `closed`                            |
| `block`   | `<from_id> <to_id>` `--type`                                                    | Declare a dependency edge between two issues           |
| `comment` | `<id>` `--body` `--author`                                                      | Append a comment to an issue                            |
| `log`     | `[id]`                                                                          | Event history — global if no ID, per-issue otherwise   |

---

## `init` — Deep Dive

```
po init [--author <name>] [--email <email>] [--project <name>] [--desc <text>] [--force] [--no-git-check]
```

All flags are optional:

- `--author` / `--email` — default to `git config user.name` / `user.email` if omitted.
- `--project` — defaults to the current directory's name.
- `--desc` — project description; stored as `null` if omitted.
- `--force` — drops and recreates all tables, wiping any existing data.
- `--no-git-check` — skips the prompt asking whether to `git init` the project if git isn't already set up.

Running `init` writes `.po/config.json` (author, email, project, description, database path) and creates the four SQLite tables described in [Data Model](#data-model) below.

---

## `create` — Deep Dive

The only required flag is `--title`. Everything else is optional and has a sensible default.

```
po create --title <text> [--type <type>] [--priority <0-3>] [--desc <text>] [--parent <id>]
```

### Flags

#### `--title` (required)

The issue title. Keep it imperative and specific. The title is the primary field shown in `list` output, so it should read clearly in a table column.

```
po create --title "Add FTS5 search to list command"
po create --title "Decide on output format for show"
po create --title "Auth middleware returns 500 on expired token"
```

---

#### `--type` (default: `task`, choices: `task | bug | feature | chore`)

This is where most of the semantic weight lives. The type isn't cosmetic — it tells you and any agent *how to process this issue*. `argparse` enforces the four values below; anything else is rejected at the CLI.

| Type      | What it is | When `close`d means |
|-----------|------------|----------------------|
| `task`    | A discrete unit of work with a clear deliverable. The default. | The code is shipped or the thing is done. |
| `bug`     | Something that's broken and needs to be fixed. Implies regression — something that *was* working isn't. | The regression is resolved and verified. |
| `feature` | New capability that doesn't exist yet. Distinct from `task` because it has a user-facing outcome. | The capability is working and observable. |
| `chore`   | Maintenance work with no direct user-facing outcome (deps, tooling, cleanup). | The maintenance work is done. |

**Practical guidance:**

- If you're not sure, use `task`. The type system only earns its keep when you're actually filtering by it.
- There's no dedicated `epic` type yet — hierarchy is modeled purely with `--parent`, regardless of the parent issue's `type`. Create the container issue first (any type), then create children with `--parent <id>`.

---

#### `--priority` (default: `2`)

Numeric. Lower is more urgent.

| Value | Label    | When to use |
|-------|----------|-------------|
| `0`   | critical | Blocking everything. Must be resolved before any other work. |
| `1`   | high     | Should be next in the queue. High impact or time-sensitive. |
| `2`   | medium   | Normal work. The default. |
| `3`   | low      | Nice to have. Won't get to it soon. |

Priority is a sort hint, not a strict queue. `po list` sorts by priority ascending by default, so critical issues surface first.

---

#### `--desc` (optional)

Long-form context. Not shown in `list` output — only in `show`. Use it for:

- Acceptance criteria on a `feature`
- Reproduction steps on a `bug`
- Maintenance notes on a `chore`
- Links to relevant files or prior issues

If `--desc` is more than a sentence, it's doing real work.

---

#### `--parent` (optional)

The ID of an existing issue this one belongs to (any type — there's no dedicated `epic` type). Inserts a `parent` edge in the `dependencies` table automatically. You don't need to call `po block` separately.

```
po create --title "Build auth system" --type task
# → 63e9bf created

po create --title "Implement JWT generation" --type task --parent 63e9bf
po create --title "Write token refresh logic" --type task --parent 63e9bf
po create --title "Handle token expiry" --type chore --parent 63e9bf
```

`po show 63e9bf` will list all children. `po list --type task` will show them in the main queue.

---

### Full Example

```
po create \
  --title "Add FTS5 search to list command" \
  --type feature \
  --priority 1 \
  --desc "Wire a --search flag into `po list` backed by SQLite FTS5. Acceptance: search matches on title and desc, case-insensitive." \
  --parent 3
```

---

### Example Flows

```
# Start a new feature with child tasks
po create --title "Search capability" --type feature
# → a3f1c2 created
po create --title "Add FTS5 to SQLite schema" --type task --parent a3f1c2 --priority 1
po create --title "Wire --search flag into list command" --type task --parent a3f1c2 --priority 1
po create --title "Check FTS5 query performance on 10k issues" --type chore --parent a3f1c2 --priority 0 \
  --desc "Max 1 hour. Check MATCH syntax and query plan."

# Normal task flow
po ready b7d92e
po close b7d92e
po list --status open
```

---

## Data Model

Four tables. Issue IDs are 6-character SHA-256 hex prefixes derived from the issue's content fields.

### issues

| Column     | Type    | Notes                                          |
|------------|---------|------------------------------------------------|
| hash_id    | TEXT    | Primary key; 6-char SHA-256 prefix             |
| title      | TEXT    | Required                                       |
| desc       | TEXT    | Optional long-form                             |
| status     | TEXT    | Default `open`; see status vocabulary below    |
| type       | TEXT    | Default `task`; see type vocabulary below      |
| priority   | INTEGER | Default `2`; 0 = critical … 3 = low           |
| parent     | TEXT    | FK → issues.hash_id; set by `--parent`         |
| created_at | TEXT    | ISO 8601, set on insert                        |
| updated_at | TEXT    | ISO 8601, null until first update              |

### dependencies

| Column  | Type    | Notes                                         |
|---------|---------|-----------------------------------------------|
| from_id | TEXT    | (PK) FK → issues.hash_id (the issue that does blocking)|
| to_id   | TEXT    | (PK) FK → issues.hash_id (the issue being blocked)     |
| type    | TEXT    | (PK) See edge type vocabulary below, default is blocks              |

### comments

| Column     | Type    | Notes                       |
|------------|---------|-----------------------------|
| id         | INTEGER | Primary key                     |
| issue_id   | TEXT    | FK → issues.hash_id             |
| body       | TEXT    | Required                        |
| author     | TEXT    | Optional                        |
| created_at | TEXT    | ISO 8601                        |

### events

| Column     | Type    | Notes                                                    |
|------------|---------|----------------------------------------------------------|
| id         | INTEGER | Primary key                                             |
| issue_id   | TEXT    | FK → issues.hash_id                                    |
| action     | TEXT    | e.g. `created`, `status_changed`, `commented`, `blocked`|
| payload    | TEXT    | JSON string with before/after values                   |
| created_at | TEXT    | ISO 8601                                               |

---

## Vocabularies

### Status

| Value         | Meaning                                       |
|---------------|-----------------------------------------------|
| `open`        | Not started                                  |
| `in_progress` | Being worked on (set by `ready`)             |
| `blocked`     | Cannot proceed; has an unresolved blocker    |
| `deferred`    | Intentionally postponed                      |
| `closed`      | Done (set by `close`)                        |

### Issue Type

| Value      | Default status behavior                           |
|------------|---------------------------------------------------|
| `task`     | Normal flow: open → in_progress → closed         |
| `bug`      | Normal flow. Implies a regression, not new work  |
| `feature`  | Normal flow. Has a user-facing outcome           |
| `chore`    | Normal flow. No direct user-facing outcome       |

### Dependency Edge Types

| Type      | Meaning                                                |
|-----------|--------------------------------------------------------|
| `blocks`  | `from_id` must be resolved before `to_id` can proceed |
| `parent`  | `from_id` is a child of `to_id` (hierarchy, e.g. a container issue's sub-tasks) |
| `related` | Soft link — informational, no enforcement             |

---

## How Beads Influenced This Design

| Beads                              | This tool                                        |
|------------------------------------|--------------------------------------------------|
| Dolt (versioned SQL)               | SQLite — simpler, no version history             |
| Content-hash IDs (`bd-a1b2`)       | Content-hash IDs (`63e9bf`)                 |
| 7 status values incl. `pinned`, `hooked` | 5 status values — leaner vocabulary        |
| Multi-machine sync via DoltHub     | Single machine, no sync layer                   |
| Embedded vs server mode            | Always embedded                                  |
| 12 issue types                     | 4 types — dropped `epic`, `decision` (redundant with `task`)    |
| `metadata` JSON field              | Not included initially — add when needed         |

The core idea from beads that carries over unchanged: **every issue is a node, every dependency is a typed edge**. The graph is the source of truth for what's blocked and why.

---
