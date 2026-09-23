from core.commands.init import initialize_po

def register(sub):
    init = sub.add_parser("init", help="initialize po and configure settings")
    init.add_argument("--project", type=str, help="project name")
    init.add_argument("--author", type=str, help="author")
    init.add_argument("--email", type=str, help="author")
    init.add_argument("--desc", type=str, help="description of project")
    init.add_argument("--backend", type=str,choices=["sqlite","postgresql"], default="sqlite")
    init.add_argument("--force", action="store_true", help="overwrites any previous init command")
    init.add_argument("--no-git-check", action="store_true", help="ignore if git has been initialized")

    init.set_defaults(func=handle)


def handle(args):
    initialized = initialize_po(author=args.author, email=args.email, project=args.project, desc = args.desc, backend = args.backend, force=args.force, no_git_check=args.no_git_check)

    print("successfully initialized")