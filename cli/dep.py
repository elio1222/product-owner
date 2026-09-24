from core.commands.dep import block_issues

def register(sub):
    p = sub.add_parser("dep", help="declare a dependency edge between two issues")
    p.add_argument("from_id", type=str, help="issue that is blocking")
    p.add_argument("to_id", type=str, help="issue being blocked")
    p.set_defaults(func=handle)

def handle(args):
    block_issues(
        from_id=args.from_id,
        to_id=args.to_id,
    )

    print(f"{args.from_id} now blocks {args.to_id}")
