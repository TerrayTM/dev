import os
import shutil
import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.tasks.task import Task


class UninstallTask(Task):
    def _perform(self, _: Namespace) -> int:
        module = os.path.basename(os.getcwd())

        subprocess.check_call(["pip", "uninstall", "-y", module])
        shutil.rmtree(f"{module}.egg-info")

        return RC_OK
