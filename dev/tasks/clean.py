import shutil
from pathlib import Path

from dev.constants import ReturnCode
from dev.tasks.task import Task


class CleanTask(Task):
    def _perform(self) -> int:
        for file in Path(".").rglob("*.py[co]"):
            file.unlink()

        for folder in Path(".").rglob("__pycache__"):
            shutil.rmtree(folder)

        return ReturnCode.OK
