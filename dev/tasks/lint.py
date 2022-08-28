from argparse import ArgumentParser, Namespace, _SubParsersAction
from io import StringIO
from pathlib import Path

import isort
from black import FileMode, InvalidInput, WriteBack, format_file_in_place

from dev.constants import RC_FAILED, RC_OK
from dev.files import filter_python_files, get_changed_repo_files, get_repo_files
from dev.tasks.task import Task


class LintTask(Task):
    def _perform(self, args: Namespace) -> int:
        get_files_function = get_repo_files if args.all else get_changed_repo_files
        files = get_files_function([filter_python_files])
        write_back = WriteBack.NO if args.validate else WriteBack.YES
        output = StringIO() if args.validate else None
        formatted = []

        for file in files:
            try:
                if format_file_in_place(
                    Path(file), False, FileMode(), write_back
                ) | isort.file(file, output=output, profile="black", quiet=True):
                    formatted.append(file)
            except InvalidInput:
                print(f"Cannot parse Python file '{file}'.")
                return RC_FAILED

        if len(formatted) > 0:
            if args.validate:
                print("The following files are misformatted:")
                for file in formatted:
                    print(f"  - {file}")

                return RC_FAILED

            print(
                f"Checked {len(files)} file{'s' if len(files) > 1 else ''} and "
                f"formatted {len(formatted)} file{'s' if len(formatted) > 1 else ''}."
            )

        return RC_OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("--all", action="store_true", dest="all")
        parser.add_argument("--validate", action="store_true", dest="validate")

        return parser
