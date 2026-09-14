from core.commands.update import update_issue

def register(sub):
    p = sub.add_parser("update", help="update a specific issue on hand")
    p.add_argument("id", type=str, help="issue id")
    p.add_argument("--status", type=str, help="status of issue")
    p.set_defaults(func=handle)

def handle(args):
    update_issue(
        id=args.id,
        status=args.status,
    )
