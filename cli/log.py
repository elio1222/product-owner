from core.commands.log import get_log

def register(sub):
    p = sub.add_parser("log", help="event history")
    p.add_argument("id", nargs="?", type=str, help="issue id (omit for global log)")
    p.set_defaults(func=handle)

def handle(args):
    get_log(id=args.id)
