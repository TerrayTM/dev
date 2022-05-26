import os
import subprocess
from argparse import Namespace

from dev.constants import RC_OK
from dev.task import Task


class CountTask(Task):
    def _perform(self, _: Namespace) -> int:
        print(
            sum(
                sum(1 for _ in open(os.path.abspath(file)))
                for file in filter(
                    None,
                    subprocess.check_output(["git", "ls-files"])
                    .decode("utf-8")
                    .split("\n"),
                )
            )
        )

        return RC_OK
