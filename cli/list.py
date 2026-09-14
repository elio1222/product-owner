from core.commands.list import list_issues

def register(sub):
    p = sub.add_parser("list", help="list all the issues")
    p.add_argument("--status", type=str, help="type of status you want to filter with")
    p.add_argument("--type", type=str, help="")
    p.add_argument("--blocked", help="list blocked issues that are currently 'stuck'")
    p.set_defaults(func=handle)

def handle(args):
    list_issues(
        status=args.status,
        type=args.type,
        blocked=args.blocked,
    )
