from core.commands.close import close_issue

def register(sub):
    p = sub.add_parser("close", help="close issue")
    p.add_argument("id", type=str, help="issue id")
    p.set_defaults(func=handle)

def handle(args):
    close_issue(id=args.id)
