import math
import subprocess
from argparse import ArgumentParser, _SubParsersAction
from typing import List

from dev.constants import ReturnCode
from dev.output import output
from dev.tasks.task import Task
from dev.timer import measure_time


class TimeTask(Task):
    def _perform(self, command: List[str], count: int = 1) -> int:
        if count <= 0:
            output("Number of iterations must be a positive number.")
            return ReturnCode.FAILED

        best = math.inf

        for _ in range(count):
            best = min(
                best,
                measure_time(
                    subprocess.run,
                    command,
                    raise_exception=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).elapsed,
            )
            output(".", end="", flush=True)

        output()
        output(f"Best of {count} trial{'s' if count > 1 else ''} is {round(best, 3)}s.")

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-c", "--count", type=int, default=1)
        parser.add_argument("command", nargs="+")

        return parser
