from core.commands.update import update_issue

def register(sub):
    p = sub.add_parser("update", help="update a specific issue on hand")
    p.add_argument("id", type=str, help="issue id")
    p.add_argument("--claim", action="store_true", help="claim an issue")
    p.add_argument("--status", type=str, help="update status",choices=["open", "in_progres", "blocked", "deferred", "closed"])
    p.add_argument("--title", type=str, help="update title")
    p.add_argument("--desc", type=str, help="update desc")
    p.add_argument("--type", type=str, help="update type", choices=["task", "bug", "feature", "chore"])
    p.set_defaults(func=handle)

def handle(args):
    update_issue(
        id=args.id,
        claim=args.claim,
        status=args.status,
        title=args.title,
        desc=args.desc,
        type=args.type
    )
