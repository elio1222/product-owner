from core.commands.create import create_issue

def register(sub):
    p = sub.add_parser("create", help="create a type of issue")
    p.add_argument("title",type=str, help="title of issue")
    p.add_argument("--type", type=str, default="task", help="type of task it is: task | bug | feature | chore", choices=["task", "bug", "feature", "chore"])
    p.add_argument("--priority", type=int, default=2, help="0=low 1=medium 2=high 3=critical", choices=[0, 1, 2, 3])
    p.add_argument("--desc", type=str, help="long-form description")
    p.add_argument("--parent", type=str, help="hash issue ID to attach as child")
    p.set_defaults(func=handle)

def handle(args):

    issue_id = create_issue(
        title=args.title, type=args.type, priority=args.priority, desc=args.desc, parent=args.parent
    )

    print(f"{issue_id} issue created")