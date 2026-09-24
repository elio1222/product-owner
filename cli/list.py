from core.commands.list import list_issues

def register(sub):
    p = sub.add_parser("list", help="list all the issues")
    p.add_argument("--status", type=str, help="type of status you want to filter with", choices=["open", "in_progress", "blocked", "deferred", "closed"])
    p.add_argument("--type", type=str, help="type of issue you want to filter", choices=["task", "bug", "feature", "chore"])
    p.add_argument("--priority", type=int, help="list by priority", choices=[0,1,2,3])
    p.set_defaults(func=handle)

def handle(args):
    list_issues(
        status=args.status,
        type=args.type,
        priority=args.priority
    )
