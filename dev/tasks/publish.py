import os

from dev.constants import ReturnCode
from dev.output import output
from dev.subprocess import subprocess_run
from dev.tasks.task import Task


class PublishTask(Task):
    def _perform(self) -> int:
        if not os.path.isdir("dist"):
            output("No distributions found to publish.")
            return ReturnCode.OK

        subprocess_run(["twine", "upload", "dist/*"])

        return ReturnCode.OK
