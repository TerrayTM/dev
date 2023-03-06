import os
import shutil

from dev.constants import SETUP_FILE, ReturnCode
from dev.process import run_process
from dev.tasks.task import Task


class BuildTask(Task):
    def _perform(self) -> int:
        if os.path.isdir("dist"):
            shutil.rmtree("dist")

        run_process(["python", SETUP_FILE, "sdist"])
        run_process(["twine", "check", "dist/*"])

        return ReturnCode.OK
