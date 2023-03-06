import argparse
import subprocess

from dev.constants import ReturnCode
from dev.exceptions import ConfigParseError
from dev.loader import load_tasks_from_config
from dev.output import output
from dev.tasks.index import iter_tasks
from dev.version import __version__

_CLI_FLAGS = {"version": ("-v", "--version"), "update": ("-u", "--update")}


def main() -> int:
    task_map = {}
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    group = parser.add_mutually_exclusive_group()
    subparsers = parser.add_subparsers(dest="action")

    for flags in _CLI_FLAGS.values():
        group.add_argument(*flags, action="store_true")

    for task in iter_tasks():
        task.add_to_subparser(subparsers)
        task_map[task.task_name()] = task

    try:
        config_tasks = load_tasks_from_config()
    except ConfigParseError as error:
        output(f"An error has occurred trying to read the config files:")
        output(f"  {str(error)}")
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
    if args.action:
        for name, flags in _CLI_FLAGS.items():
            if getattr(args, name):
                output(
                    f"Argument {'/'.join(flags)} is not allowed with argument 'action'."
                )
                return ReturnCode.FAILED

    if args.version:
        output(__version__)
        return ReturnCode.OK

    if args.update:
        try:
            subprocess.run(["python", "-m", "pip", "install", "-U", "dev-star"])
            return ReturnCode.OK
        except:
            return ReturnCode.FAILED

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
