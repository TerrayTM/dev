import subprocess
from argparse import ArgumentParser, Namespace, _SubParsersAction
from pathlib import Path

from dev.constants import RC_OK
from dev.task import Task


class RunTask(Task):
    def _perform(self, args: Namespace) -> int:
        entry_points = list(Path(".").rglob("main.py"))

        if len(entry_points) == 1:
            subprocess.run(
                [
                    "python",
                    "-m",
                    str(entry_points[0]).replace("\\", ".").replace(".py", ""),
                ]
                + args.args
            )
        else:
            print("Cannot automatically determine the entry point of the program.")

        return RC_OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("args", nargs="*", default=[])

        return parser
