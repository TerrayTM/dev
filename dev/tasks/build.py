import os
import shutil

from dev.constants import SETUP_FILE, ReturnCode
from dev.subprocess import subprocess_run
from dev.tasks.task import Task


class BuildTask(Task):
    def _perform(self) -> int:
        if os.path.isdir("dist"):
            shutil.rmtree("dist")

        subprocess_run(["python", SETUP_FILE, "sdist"])
        subprocess_run(["twine", "check", "dist/*"])

        return ReturnCode.OK
