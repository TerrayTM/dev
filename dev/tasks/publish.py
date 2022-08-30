import os
import subprocess

from dev.constants import RC_OK
from dev.tasks.task import Task


class PublishTask(Task):
    def _perform(self) -> int:
        if not os.path.isdir("dist"):
            print("No distributions found to publish.")
            return RC_OK

        subprocess.run(["twine", "upload", "dist/*"])

        return RC_OK
