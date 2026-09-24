from core.commands.delete import delete_issue

def register(sub):
    p = sub.add_parser("delete", help="delete an issue")
    p.add_argument("id", type=str, help="issue id")
    p.set_defaults(func=handle)

def handle(args):
    title = delete_issue(id=args.id)

    print(f"{args.id} issue deleted ({title})")
