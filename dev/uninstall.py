import os
import shutil
import subprocess

from dev.constants import RC_OK
from dev.task import Task


class UninstallTask(Task):
    def perform(self) -> int:
        module = os.path.basename(os.getcwd())

        subprocess.check_call(["pip", "uninstall", "-y", module])
        shutil.rmtree(f"{module}.egg-info")

        return RC_OK
