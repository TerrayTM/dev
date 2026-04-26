import argparse
import importlib
import pkgutil
import subprocess
from functools import cache

from dev.constants import ReturnCode
from dev.exceptions import ConfigParseError, TaskNotFoundError
from dev.loader import load_tasks_from_config
from dev.output import output
from dev.tasks.custom import CustomTask
from dev.tasks.task import TASK_MAP, DynamicTaskMap
from dev.version import __version__

_CLI_FLAGS = {"version": ("-v", "--version"), "update": ("-u", "--update")}


@cache
def _import_all_tasks() -> None:
    package_name = "dev.tasks"
    package = importlib.import_module(package_name)

    for module_info in pkgutil.iter_modules(package.__path__):
        module_name = f"{package_name}.{module_info.name}"
        importlib.import_module(module_name)


def build_dynamic_task_map() -> DynamicTaskMap:
    _import_all_tasks()

    result: DynamicTaskMap = {}
    result.update(TASK_MAP)

    config_tasks = load_tasks_from_config(result)

    for custom_task in config_tasks:
        name = custom_task.task_name()
        task = result.get(name)

        if not task or custom_task.override_existing():
            result[name] = custom_task
            continue

        assert not isinstance(task, CustomTask)
        task.customize(custom_task)

    for custom_task in config_tasks:
        custom_task.validate()

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="dev", description="Dev tools CLI for performing common development tasks."
    )
    group = parser.add_mutually_exclusive_group()
    subparsers = parser.add_subparsers(dest="action")

    for flags in _CLI_FLAGS.values():
        group.add_argument(*flags, action="store_true")

    try:
        dynamic_task_map = build_dynamic_task_map()
    except (TaskNotFoundError, ConfigParseError) as error:
        output("An error has occurred trying to read the config files:")
        output(f"  - {str(error)}")
        return ReturnCode.FAILED

    for task in dynamic_task_map.values():
        task.add_to_subparser(subparsers)

    args = parser.parse_args()
    if args.action:
        for name, flags in _CLI_FLAGS.items():
            if not getattr(args, name):
                continue
            output(f"Argument {'/'.join(flags)} is not allowed with argument 'action'.")
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
    selected_task = dynamic_task_map.get(args.action)

    if selected_task:
        rc = selected_task.execute(args, allow_extraneous_args=True)
    else:
        task_keys = dynamic_task_map.keys()
        output(f"No action is specified. Choose one from {{{', '.join(task_keys)}}}.")

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
