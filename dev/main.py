import argparse
import subprocess
from typing import Any, Dict

from dev.constants import ReturnCode
from dev.exceptions import ConfigParseError, TaskNotFoundError
from dev.loader import load_tasks_from_config
from dev.output import output
from dev.tasks.index import get_task_map
from dev.version import __version__

_CLI_FLAGS = {"version": ("-v", "--version"), "update": ("-u", "--update")}


def _build_dynamic_task_map() -> Dict[str, Any]:
    dynamic_task_map: Dict[str, Any] = get_task_map()
    config_tasks = load_tasks_from_config(dynamic_task_map)

    for custom_task in config_tasks:
        name = custom_task.task_name()
        if name in dynamic_task_map and not custom_task.override_existing():
            dynamic_task_map[name].customize(custom_task)
        else:
            dynamic_task_map[name] = custom_task

    for custom_task in config_tasks:
        custom_task.validate()

    return dynamic_task_map


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev",
        description="Dev tools CLI for performing common development tasks.",
    )
    group = parser.add_mutually_exclusive_group()
    subparsers = parser.add_subparsers(dest="action")

    for flags in _CLI_FLAGS.values():
        group.add_argument(*flags, action="store_true")

    try:
        dynamic_task_map = _build_dynamic_task_map()
    except (TaskNotFoundError, ConfigParseError) as error:
        output("An error has occurred trying to read the config files:")
        output(f"  - {str(error)}")
        return ReturnCode.FAILED

    for task in dynamic_task_map.values():
        task.add_to_subparser(subparsers)

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
        except Exception:
            return ReturnCode.FAILED

    rc = ReturnCode.OK
    task = dynamic_task_map.get(args.action)

    if task:
        rc = task.execute(args, allow_extraneous_args=True)
    else:
        task_keys = dynamic_task_map.keys()
        output(f"No action is specified. Choose one from {{{', '.join(task_keys)}}}.")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
