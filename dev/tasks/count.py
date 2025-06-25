import os
import subprocess
from argparse import ArgumentParser, _SubParsersAction

import tabulate

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
    def _perform(
        self,
        by_author: bool = False,
        verbose: bool = False,
        exclude_tests: bool = False,
    ) -> int:
        filters = [build_file_extensions_filter(CODE_EXTENSIONS)]

        if exclude_tests:
            filters.append(filter_not_unit_test_files)

        if by_author:
            authors = []

            try:
                if subprocess.run(
                    ["git", "status"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).returncode:
                    output("Count by author needs to be ran in a git repository.")
                    return ReturnCode.FAILED
            except FileNotFoundError:
                output("Count by author requires git to be installed.")
                return ReturnCode.FAILED

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

                details = {}
                for line in result.stdout.rstrip().split("\n"):
                    added, removed, path = line.split("\t")

                    if evaluate_file_filters(filters, path):
                        subtotal = int(added) - int(removed)
                        lines += subtotal
                        details[path] = details.get(path, 0) + subtotal

                output(f"{author}: {lines}")

                if verbose:
                    for path, subtotal in details.items():
                        output(f"  - {path}: {subtotal}")
        else:
            lines = 0
            details = []

            for file in get_repo_files(filters):
                subtotal = 0

                with open(file, encoding="utf8") as reader:
                    subtotal += sum(1 for _ in reader)

                details.append((subtotal, os.path.relpath(file, os.getcwd())))
                lines += subtotal

            if verbose:
                output(
                    tabulate.tabulate(
                        sorted(details, reverse=True),
                        ["lines", "path"],
                        tablefmt="outline",
                    )
                )

            output(lines)

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-b", "--by-author", action="store_true", dest="by_author")
        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose")
        parser.add_argument(
            "-e", "--exclude-tests", action="store_true", dest="exclude_tests"
        )

        return parser
