import argparse

from dev.constants import RC_OK
from dev.tasks import TASKS


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    subparsers = parser.add_subparsers(dest="action")
    task_map = {}

    for task in TASKS:
        task.add_to_subparser(subparsers)
        task_map[task.task_name()] = task

    args = parser.parse_args()
    rc = RC_OK
    task = task_map.get(args.action)

    if task:
        rc = task.execute(args)
    else:
        print(
            "No action is specified.Please choose one from "
            f"{{{', '.join(task_map.keys())}}}."
        )

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
