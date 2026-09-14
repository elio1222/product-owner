from core.commands.init import initialize_po

def register(sub):
    init = sub.add_parser("init", help="initialize po and configure settings")
    init.add_argument("--author", type=str, help="author")
    init.add_argument("--email", type=str, help="author")

    init.set_defaults(func=handle)


def handle(args):
    initialize_po()