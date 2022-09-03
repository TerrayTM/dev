from dev.exceptions import TaskNotFoundError
from dev.tasks.build import BuildTask
from dev.tasks.clean import CleanTask
from dev.tasks.count import CountTask
from dev.tasks.doc import DocTask
from dev.tasks.install import InstallTask
from dev.tasks.lint import LintTask
from dev.tasks.publish import PublishTask
from dev.tasks.run import RunTask
from dev.tasks.test import TestTask
from dev.tasks.time import TimeTask
from dev.tasks.uninstall import UninstallTask

__all__ = [
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
]

_task_map_cache = None


def get_task(name: str) -> type:
    global _task_map_cache

    if _task_map_cache is None:
        _task_map_cache = {task.task_name(): task for task in __all__}

    if name in _task_map_cache:
        return _task_map_cache[name]

    raise TaskNotFoundError()
