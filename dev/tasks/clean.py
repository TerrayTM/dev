import shutil
from pathlib import Path

from dev.constants import RC_OK
from dev.tasks.task import Task


class CleanTask(Task):
    def _perform(self) -> int:
        for file in Path(".").rglob("*.py[co]"):
            file.unlink()

        for folder in Path(".").rglob("__pycache__"):
            shutil.rmtree(folder)

        return RC_OK
