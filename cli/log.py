from core.commands.log import get_log

# po log is read-only: it shows an issue's history (created, updated, closed, comments), oldest first.
# Without an id it shows the history of every issue.

def register(sub):
    p = sub.add_parser("log", help="history of an issue")
    p.add_argument("id", nargs="?", type=str, help="issue id (omit for global log)")
    p.add_argument("--limit", type=int, help="only show the most recent N entries")
    p.set_defaults(func=handle)

def handle(args):
    get_log(id=args.id, limit=args.limit)
