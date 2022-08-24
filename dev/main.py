import argparse

import dev.tasks
from dev.constants import CONFIG_FILE, RC_FAILED, RC_OK
from dev.exceptions import ConfigParseError
from dev.loader import load_tasks_from_config


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    subparsers = parser.add_subparsers(dest="action")
    task_map = {}

    for task in dev.tasks.__all__:
        task.add_to_subparser(subparsers)
        task_map[task.task_name()] = task

    try:
        config_tasks = load_tasks_from_config()
    except ConfigParseError:
        print(f"An error has occurred trying to read {CONFIG_FILE} config file.")
        return RC_FAILED

    for name, custom_task in config_tasks:
        if name in task_map:
            if custom_task.override_existing():
                task_map[name] = custom_task
            else:
                task_map[name].customize(custom_task)
        else:
            subparsers.add_parser(name)
            task_map[name] = custom_task

    args = parser.parse_args()
    rc = RC_OK
    task = task_map.get(args.action)

    if task:
        rc = task.execute(args)
    else:
        print(
            f"No action is specified. Choose one from {{{', '.join(task_map.keys())}}}."
        )

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
