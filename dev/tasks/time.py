import math
import subprocess
import time
from argparse import ArgumentParser, _SubParsersAction
from typing import List

from dev.constants import ReturnCode
from dev.output import output
from dev.tasks.task import Task


class TimeTask(Task):
    def _perform(self, command: List[str], times: int = 10) -> int:
        best = math.inf

        for _ in range(times):
            start = time.monotonic()
            subprocess.run(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            best = min(best, time.monotonic() - start)
            output(".", end="", flush=True)

        output()
        output(f"Best of {times} trials is {round(best, 3)}s.")

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-t", "--times", type=int, default=10)
        parser.add_argument("command", nargs="+")

        return parser
