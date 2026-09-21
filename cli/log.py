from core.commands.log import get_log

# po log will showcase all the events that occured with a specific issue id, users will only have the option to have it as a read command.
# po log will showcase things like status changes, comments done to issue, and paylod with before/after values

def register(sub):
    p = sub.add_parser("log", help="event history of an issue")
    p.add_argument("id", nargs="?", type=str, help="issue id (omit for global log)")
    p.set_defaults(func=handle)

def handle(args):
    get_log(id=args.id)
