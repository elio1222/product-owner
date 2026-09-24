from core.commands.ready import ready_issue

def register(sub):
    p = sub.add_parser("ready", help="view all issues that are ready to begin working on ")
    p.set_defaults(func=handle)

def handle(args):
    ready_issue()
