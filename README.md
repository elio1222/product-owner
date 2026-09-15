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
│   ├── done.py
│   ├── block.py
│   ├── comment.py
│   └── log.py
├── core/            # business logic, no argparse here
│   ├── commands/    # cli logic
│   |    ├── *.py    # logic for each subcommand in cli/ 
│   ├── db.py        # SQLite connection, schema migrations
│   ├── schemas.py   # Pydantic Models: Issue
│   └── queries.py   # reusable SQL helpers
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

## Commands

| Command   | Arguments / Flags                                       | Purpose                                               |
|-----------|---------------------------------------------------------|-------------------------------------------------------|
| `init`    | —                                                       | Create `.po/db.sqlite` and run schema migrations      |
| `create`  | `--title` `--type` `--priority` `--desc` `--parent`  | Create a new issue; prints assigned ID  |
| `list`    | `--status` `--type` `--blocked`            | Tabular list with optional filters                   |
| `show`    | `<id>`                                                  | Full issue detail: fields, dependencies, comments    |
| `update`  | `<id>` + any field flag from `create`                   | Patch any field on an existing issue                 |
| `ready`   | `<id>`                                                  | Shortcut: status → `in_progress`                     |
| `close`    | `<id>`                                                  | Shortcut: status → `closed`                          |
| `block`   | `<from-id> <to-id>` `--type`                            | Declare a dependency edge between two issues         |
| `comment` | `<id>` `--body` `--author`                              | Append a comment to an issue                         |
| `log`     | `[id]`                                                  | Event history — global if no ID, per-issue otherwise |

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

#### `--type` (default: `task`)

This is where most of the semantic weight lives. The type isn't cosmetic — it tells you and any agent *how to process this issue*. A `spike` has a time constraint and produces knowledge, not code. A `decision` is a permanent record, not a to-do. An `epic` is a container, never work itself.

Without type, everything looks like a task and you lose that signal. With type, `po list --type spike` gives you all your open research threads, `po list --type decision` is your architecture log.

| Type       | What it is | When `done` means |
|------------|------------|-------------------|
| `task`     | A discrete unit of work with a clear deliverable. The default. | The code is shipped or the thing is done. |
| `bug`      | Something that's broken and needs to be fixed. Implies regression — something that *was* working isn't. | The regression is resolved and verified. |
| `feature`  | New capability that doesn't exist yet. Distinct from `task` because it has a user-facing outcome. | The capability is working and observable. |

**Practical guidance:**

- If you're not sure, use `task`. The type system only earns its keep when you're actually filtering by it.
- `epic` + `--parent` is how you model hierarchy. Create the epic first, then create tasks with `--parent <epic-id>`.
- `spike` should almost always have a `--desc` with a time box: `"Max 2 hours. Goal: understand SQLite FTS5 query performance."`.
- `decision` issues work well as a lightweight ADR (Architecture Decision Record). Write the reasoning in `--desc`.

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
- Time box and goal on a `spike`
- Full reasoning on a `decision`
- Links to relevant files or prior issues

If `--desc` is more than a sentence, it's doing real work.

---

#### `--parent` (optional)

The ID of an `epic` this issue belongs to. Inserts a `parent` edge in the `dependencies` table automatically. You don't need to call `po block` separately.

```
po create --title "Build auth system" --type epic
# → 63e9bf created

po create --title "Implement JWT generation" --type task --parent 63e9bf
po create --title "Write token refresh logic" --type task --parent 63e9bf
po create --title "Decide on token expiry duration" --type decision --parent 63e9bf
```

`po show 63e9bf` will list all children. `po list --type task` will show them in the main queue.

---

### Full Example

```
po create \
  --title "Decide on output format for po show" \
  --type decision \
  --priority 1 \
  --desc "Options: plain key-value, a rich table, or JSON for agent consumption. Pick one format and document why. Consider that agents need parseable output." \
  --parent 3
```

---

### Example Flows

```
# Start a new feature with child tasks
po create --title "Search capability" --type epic
# → a3f1c2 created
po create --title "Add FTS5 to SQLite schema" --type task --parent a3f1c2 --priority 1
po create --title "Wire --search flag into list command" --type task --parent a3f1c2 --priority 1
po create --title "Spike: FTS5 query performance" --type spike --parent a3f1c2 --priority 0 \
  --desc "Max 1 hour. How does FTS5 perform on 10k issues? Check MATCH syntax."

# Normal task flow
po ready b7d92e
po done b7d92e
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
| id      | INTEGER | Primary key                                       |
| from_id | TEXT    | FK → issues.hash_id (the issue that does blocking)|
| to_id   | TEXT    | FK → issues.hash_id (the issue being blocked)     |
| type    | TEXT    | See edge type vocabulary below               |

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
| `closed`      | Done (set by `done`)                         |

### Issue Type

| Value      | Default status behavior                           |
|------------|---------------------------------------------------|
| `task`     | Normal flow: open → in_progress → closed         |
| `bug`      | Normal flow. Implies a regression, not new work  |
| `feature`  | Normal flow. Has a user-facing outcome           |
| `chore`    | Normal flow. Has a user-facing outcome           |

### Dependency Edge Types

| Type      | Meaning                                                |
|-----------|--------------------------------------------------------|
| `blocks`  | `from_id` must be resolved before `to_id` can proceed |
| `parent`  | `from_id` is a child of `to_id` (epic decomposition) |
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
