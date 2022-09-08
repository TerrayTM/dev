import math
import subprocess
from argparse import ArgumentParser, _SubParsersAction
from typing import List

from dev.constants import ReturnCode
from dev.output import output
from dev.tasks.task import Task
from dev.timer import measure_time


class TimeTask(Task):
    def _perform(self, command: List[str], times: int = 10) -> int:
        if times <= 0:
            output("Number of iterations must be a positive number.")
            return ReturnCode.FAILED

        best = math.inf

        for _ in range(times):
            best = min(
                best,
                measure_time(
                    subprocess.run,
                    command,
                    raise_exception=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).elasped,
            )
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
