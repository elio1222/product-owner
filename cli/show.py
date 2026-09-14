from core.commands.show import show_issue

def register(sub):
    p = sub.add_parser("show", help="show specific issue id")
    p.add_argument("id", type=str, help="issue id")
    p.set_defaults(func=handle)

def handle(args):
    show_issue(id=args.id)
