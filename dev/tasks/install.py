import subprocess

from dev.constants import RC_OK
from dev.tasks.task import Task


class InstallTask(Task):
    def _perform(self) -> int:
        subprocess.check_call(["python", "setup.py", "develop", "--no-deps"])

        return RC_OK
