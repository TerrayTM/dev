import os
import subprocess
from argparse import ArgumentParser, Namespace, _SubParsersAction

from dev.constants import RC_OK
from dev.tasks.task import Task


class CountTask(Task):
    def _perform(self, args: Namespace) -> int:
        default_filter = lambda file: file and file.endswith(".py")
        file_filter = default_filter
        lines = 0

        if args.exclude_tests:
            file_filter = lambda file: default_filter(file) and not os.path.basename(
                file
            ).startswith("test_")

        for file in filter(
            file_filter,
            subprocess.check_output(["git", "ls-files"]).decode("utf-8").split("\n"),
        ):
            with open(file) as reader:
                lines += sum(1 for _ in reader)

        print(lines)

        return RC_OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "--exclude-tests", action="store_true", dest="exclude_tests"
        )

        return parser
