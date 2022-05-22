from pathlib import Path

from dev.constants import RC_OK
from dev.task import Task


class CleanTask(Task):
    def perform(self):
        for file in Path(".").rglob("*.py[co]"):
            file.unlink()

        for folder in Path(".").rglob("__pycache__"):
            folder.rmdir()

        return RC_OK
