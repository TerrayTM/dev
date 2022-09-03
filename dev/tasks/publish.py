import os
import subprocess

from dev.constants import ReturnCode
from dev.output import output
from dev.tasks.task import Task


class PublishTask(Task):
    def _perform(self) -> int:
        if not os.path.isdir("dist"):
            output("No distributions found to publish.")
            return ReturnCode.OK

        subprocess.run(["twine", "upload", "dist/*"])

        return ReturnCode.OK
