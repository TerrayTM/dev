import os
import shutil
import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.tasks.task import Task


class UninstallTask(Task):
    def _perform(self, _: Namespace) -> int:
        module = os.path.basename(os.getcwd())
        egg_folder = f"{module}.egg-info"

        subprocess.check_call(["pip", "uninstall", "-y", module])

        if os.path.isdir(egg_folder):
            shutil.rmtree(egg_folder)

        return RC_OK