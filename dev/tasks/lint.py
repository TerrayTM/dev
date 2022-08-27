from argparse import ArgumentParser, Namespace, _SubParsersAction
from pathlib import Path

import isort
from black import FileMode, WriteBack, format_file_in_place

from dev.constants import RC_OK
from dev.files import filter_python_files, get_changed_repo_files, get_repo_files
from dev.tasks.task import Task


class LintTask(Task):
    def _perform(self, args: Namespace) -> int:
        get_files_function = get_repo_files if args.all else get_changed_repo_files
        files = get_files_function([filter_python_files])
        formatted = 0

        for file in files:
            if format_file_in_place(
                Path(file), False, FileMode(), WriteBack.YES
            ) | isort.file(file, profile="black"):
                formatted += 1

        if formatted > 0:
            print(
                f"Checked {len(files)} file{'s' if len(files) > 1 else ''} and "
                f"formatted {formatted} file{'s' if formatted > 1 else ''}."
            )

        return RC_OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("--all", action="store_true", dest="all")

        return parser
