import os
import shutil
import subprocess

from dev.constants import ReturnCode
from dev.tasks.task import Task


class UninstallTask(Task):
    def _perform(self) -> int:
        module = os.path.basename(os.getcwd())
        egg_folder = f"{module}.egg-info"

        subprocess.check_call(["pip", "uninstall", "-y", module])

        if os.path.isdir(egg_folder):
            shutil.rmtree(egg_folder)

        return ReturnCode.OK
