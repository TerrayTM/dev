import subprocess
from argparse import ArgumentParser, _SubParsersAction

from dev.constants import CODE_EXTENSIONS, ReturnCode
from dev.files import (
    build_file_extensions_filter,
    evaluate_file_filters,
    filter_not_unit_test_files,
    get_repo_files,
)
from dev.output import output
from dev.tasks.task import Task


class CountTask(Task):
    def _perform(self, by_author: bool = False, exclude_tests: bool = False) -> int:
        filters = [build_file_extensions_filter(CODE_EXTENSIONS)]

        if exclude_tests:
            filters.append(filter_not_unit_test_files)

        if by_author:
            authors = []
            authors_process = subprocess.run(
                ["git", "shortlog", "--summary", "--numbered", "--email"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="utf8",
            )

            for line in authors_process.stdout.rstrip().split("\n"):
                parts = [part for part in line.split() if len(part.strip()) > 0]
                authors.append(" ".join(parts[1:]))

            for author in authors:
                lines = 0
                result = subprocess.run(
                    [
                        "git",
                        "log",
                        f"--author={author}",
                        "--pretty=tformat:",
                        "--numstat",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    encoding="utf8",
                )

                for line in result.stdout.rstrip().split("\n"):
                    added, removed, path = line.split("\t")

                    if evaluate_file_filters(filters, path):
                        lines += int(added) - int(removed)

                output(f"{author}: {lines}")
        else:
            lines = 0
            for file in get_repo_files(filters):
                with open(file, encoding="utf8") as reader:
                    lines += sum(1 for _ in reader)

            output(lines)

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-b", "--by-author", action="store_true", dest="by_author")
        parser.add_argument(
            "-e", "--exclude-tests", action="store_true", dest="exclude_tests"
        )

        return parser
