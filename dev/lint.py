import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.task import Task


class LintTask(Task):
    def _perform(self, _: Namespace) -> int:
        subprocess.check_call(["black", "."])
        subprocess.check_call(["isort", "."])

        return RC_OK
