from argparse import ArgumentParser, Namespace, _SubParsersAction

from dev.constants import RC_OK
from dev.files import (
    filter_not_python_unit_test_files,
    filter_python_files,
    get_repo_files,
)
from dev.tasks.task import Task


class CountTask(Task):
    def _perform(self, args: Namespace) -> int:
        filters = [filter_python_files]
        lines = 0

        if args.exclude_tests:
            filters.append(filter_not_python_unit_test_files)

        for file in get_repo_files(filters):
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
