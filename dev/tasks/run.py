from argparse import ArgumentParser, _SubParsersAction
from pathlib import Path
from typing import List, Optional

from dev.constants import ReturnCode
from dev.output import output
from dev.process import run_process
from dev.tasks.task import Task


class RunTask(Task):
    def _perform(self, args: Optional[List[str]] = None) -> int:
        entry_points = list(Path(".").rglob("main.py"))

        if len(entry_points) == 1:
            run_process(
                [
                    "python",
                    "-m",
                    str(entry_points[0]).replace("\\", ".").replace(".py", ""),
                ]
                + ([] if args is None else args)
            )
        else:
            output("Cannot automatically determine the entry point of the program.")

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("args", nargs="*", default=[])

        return parser
