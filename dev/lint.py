import subprocess

from dev.constants import RC_OK
from dev.task import Task


class LintTask(Task):
    def perform(self) -> int:
        subprocess.check_call(["black", "."])
        subprocess.check_call(["isort", "-y"])

        return RC_OK
