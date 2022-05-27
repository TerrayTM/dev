import os
import shutil
import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.task import Task


class BuildTask(Task):
    def _perform(self, _: Namespace) -> int:
        if os.path.isdir("dist"):
            shutil.rmtree("dist")

        subprocess.run(["python", "setup.py", "sdist"])
        subprocess.run(["twine", "check", "dist/*"])

        return RC_OK
