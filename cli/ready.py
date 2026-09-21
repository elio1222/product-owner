from core.commands.ready import ready_issue

def register(sub):
    p = sub.add_parser("ready", help="view all issues that are ready to begin working on ")
    p.add_argument("id", type=str, help="issue id")
    p.set_defaults(func=handle)

def handle(args):
    ready_issue(id=args.id)
