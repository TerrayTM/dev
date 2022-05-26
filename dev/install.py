import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.task import Task


class InstallTask(Task):
    def _perform(self, _: Namespace) -> int:
        subprocess.check_call(["python", "setup.py", "develop", "--no-deps"])

        return RC_OK
