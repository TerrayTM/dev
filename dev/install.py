import subprocess

from dev.constants import RC_OK
from dev.task import Task


class InstallTask(Task):
    def perform(self) -> int:
        subprocess.check_call(["python", "setup.py", "develop", "--no-deps"])

        return RC_OK
