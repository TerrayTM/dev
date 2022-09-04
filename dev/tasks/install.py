import subprocess
from argparse import ArgumentParser, _SubParsersAction

from dev.constants import ReturnCode
from dev.tasks.task import Task


class InstallTask(Task):
    def _perform(self, include_dependencies: bool = False) -> int:
        command = ["python", "setup.py", "develop"]

        if not include_dependencies:
            command.append("--no-deps")

        subprocess.check_call(command)
        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-i",
            "--include-dependencies",
            action="store_true",
            dest="include_dependencies",
        )

        return parser
