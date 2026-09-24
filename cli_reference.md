# po CLI Reference

Usage: `po <command> [arguments] [flags]`

- `<arg>` required, `[arg]` optional
- Issue IDs are 6-character hex (e.g. `a3f1c2`)
- Status: `open`, `in_progress`, `blocked`, `deferred`, `closed`
- Type: `task`, `bug`, `feature`, `chore`
- Priority: `0`-`3`

## Commands

| Command | Usage | What it does |
|---|---|---|
| `init` | `po init [--project NAME] [--author NAME] [--email EMAIL] [--desc TEXT] [--force] [--no-git-check]` | Set up `.po/` in the current directory |
| `create` | `po create <title> [--type T] [--priority N] [--desc TEXT] [--parent ID]` | Create an issue. Title must be unique. Defaults: type `task`, priority `2`. `--parent` marks the new issue `blocked` |
| `list` | `po list [--status S] [--type T] [--priority N]` | List issues, closed hidden unless `--status closed` |
| `show` | `po show <id>` | Show one issue in full |
| `update` | `po update <id> [--claim] [--status S] [--title TEXT] [--desc TEXT] [--type T]` | Change fields. `--claim` sets `in_progress` |
| `ready` | `po ready` | List `open` issues |
| `close` | `po close <id> [--reason TEXT]` | Close an issue |
| `delete` | `po delete <id>` | Delete an issue |
| `dep` | `po dep <from_id> <to_id>` | `from_id` blocks `to_id` |
| `comment` | `po comment <id> <body> [--author NAME]` | Add a comment |
| `log` | `po log [id] [--limit N]` | Show history for one issue, or all |

## Known issues

- `init` drops and recreates all tables every run, deleting existing data.
- `--backend postgresql` is accepted but not implemented.
- `update --status in_progress` is rejected (typo `in_progres` in `cli/update.py`). Use `--claim`.
- `close --reason` is accepted but ignored.
- `list` combines filters with OR when one or two are given, AND only when all three are given.
- `--priority` direction is inconsistent: the help text says 0 = low, the README says 0 = critical, and `list` sorts 0 first.
- `log` has no before/after values; nothing writes to the `events` table.
