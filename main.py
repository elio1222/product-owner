import argparse
from cli import dep, init, create, list, show, update, ready, close, comment, log, delete

def main():
    parser = argparse.ArgumentParser(
        prog="po",
        description="Dependency-aware issue tracker"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    init.register(sub)
    create.register(sub)
    list.register(sub)
    show.register(sub)
    update.register(sub)
    ready.register(sub)
    close.register(sub)
    dep.register(sub)
    comment.register(sub)
    log.register(sub)
    delete.register(sub)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
