import argparse
import subprocess

from dev.constants import CONFIG_FILE, ReturnCode
from dev.exceptions import ConfigParseError
from dev.loader import load_tasks_from_config
from dev.output import output
from dev.tasks.index import iter_tasks
from dev.version import __version__


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    parser.add_argument("-v", "--version", action="store_true", dest="show_version")
    subparsers = parser.add_subparsers(dest="action")
    task_map = {}

    try:
        if subprocess.run(
            ["git", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        ).returncode:
            output("dev can only be ran in a git repository.")
            return ReturnCode.FAILED
    except FileNotFoundError:
        output("dev requires git to be installed.")
        return ReturnCode.FAILED

    for task in iter_tasks():
        task.add_to_subparser(subparsers)
        task_map[task.task_name()] = task

    try:
        config_tasks = load_tasks_from_config()
    except ConfigParseError:
        output(f"An error has occurred trying to read {CONFIG_FILE} config file.")
        return ReturnCode.FAILED

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
    if args.show_version:
        if args.action:
            output("Cannot specify the version flag along with an action.")
            return ReturnCode.FAILED

        output(__version__)
        return ReturnCode.OK

    rc = ReturnCode.OK
    task = task_map.get(args.action)

    if task:
        rc = task.execute(args, allow_extraneous_args=True)
    else:
        output(
            f"No action is specified. Choose one from {{{', '.join(task_map.keys())}}}."
        )

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
