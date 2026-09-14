from core.commands.comment import add_comment

def register(sub):
    p = sub.add_parser("comment", help="comment on an issue")
    p.add_argument("id", type=str, help="issue id")
    p.add_argument("--body", type=str, help="body of comment")
    p.add_argument("--author", type=str, help="who authored the comment")
    p.set_defaults(func=handle)

def handle(args):
    add_comment(
        id=args.id,
        body=args.body,
        author=args.author,
    )
