import os
from argparse import ArgumentParser, _SubParsersAction

from dev.constants import SETUP_FILE, ReturnCode
from dev.output import output
from dev.process import run_process
from dev.setup import parse_setup_file
from dev.tasks.task import Task


class InstallTask(Task):
    def _perform(
        self, include_dependencies: bool = False, dependencies_only: bool = False
    ) -> int:
        command = ["python", SETUP_FILE, "develop"]

        if not include_dependencies:
            command.append("--no-deps")

        if dependencies_only:
            if not os.path.isfile(SETUP_FILE):
                output("Cannot find package setup file.")
                return ReturnCode.FAILED

            setup_data = parse_setup_file(SETUP_FILE)

            if setup_data is None:
                output("Failed to parse package setup file.")
                return ReturnCode.FAILED

            if not len(setup_data.install_requires):
                return ReturnCode.OK

            command = ["pip", "install"] + setup_data.install_requires

        run_process(command, check_call=True)

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-d", "--dependencies-only", action="store_true", dest="dependencies_only",
        )
        parser.add_argument(
            "-i",
            "--include-dependencies",
            action="store_true",
            dest="include_dependencies",
        )

        return parser
