from functools import cache
from typing import Dict, Iterator, Type

from dev.exceptions import TaskNotFoundError
from dev.tasks.build import BuildTask
from dev.tasks.chain import ChainTask
from dev.tasks.clean import CleanTask
from dev.tasks.count import CountTask
from dev.tasks.doc import DocTask
from dev.tasks.install import InstallTask
from dev.tasks.lint import LintTask
from dev.tasks.publish import PublishTask
from dev.tasks.run import RunTask
from dev.tasks.spell import SpellTask
from dev.tasks.task import Task
from dev.tasks.test import TestTask
from dev.tasks.time import TimeTask
from dev.tasks.uninstall import UninstallTask

_all_tasks = [
    BuildTask,
    CleanTask,
    CountTask,
    DocTask,
    InstallTask,
    LintTask,
    PublishTask,
    RunTask,
    TestTask,
    UninstallTask,
    TimeTask,
    SpellTask,
    ChainTask,
]


@cache
def _get_task_map() -> Dict[str, Type[Task]]:
    return {task.task_name(): task for task in _all_tasks}


def get_task(name: str) -> Type[Task]:
    try:
        return _get_task_map()[name]
    except KeyError:
        raise TaskNotFoundError(f"'{name}' task cannot be found.")


def iter_tasks() -> Iterator[Type[Task]]:
    return iter(_all_tasks)
