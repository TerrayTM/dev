import os
import shutil
import subprocess

from dev.constants import RC_OK
from dev.tasks.task import Task


class BuildTask(Task):
    def _perform(self) -> int:
        if os.path.isdir("dist"):
            shutil.rmtree("dist")

        subprocess.run(["python", "setup.py", "sdist"])
        subprocess.run(["twine", "check", "dist/*"])

        return RC_OK
