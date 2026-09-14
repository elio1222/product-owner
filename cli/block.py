from core.commands.block import block_issues

def register(sub):
    p = sub.add_parser("block", help="declare a dependency edge between two issues")
    p.add_argument("from_id", type=int, help="issue that is blocking")
    p.add_argument("to_id", type=int, help="issue being blocked")
    p.add_argument("--type", type=str, default="blocks", help="blocks | parent | related")
    p.set_defaults(func=handle)

def handle(args):
    block_issues(
        from_id=args.from_id,
        to_id=args.to_id,
        type=args.type,
    )
