from argparse import ArgumentParser, _SubParsersAction
from io import StringIO
from pathlib import Path

import isort
from black import FileMode, InvalidInput, WriteBack, format_file_in_place

from dev.constants import ReturnCode
from dev.files import filter_python_files, get_changed_repo_files, get_repo_files
from dev.output import output
from dev.tasks.task import Task


class LintTask(Task):
    def _validate_character_limit(self, file: str, line: str, line_number: int) -> bool:
        if len(line) > 88:
            output(
                f"File '{file}' on line {line_number} exceeds the "
                "width limit of 88 characters."
            )
            return False

        return True

    def _validate_zero_comparison(self, file: str, line: str, line_number: int) -> bool:
        if "== 0" in line or "!= 0" in line:  # dev-star ignore
            output(f"File '{file}' on line {line_number} is comparing to zero.")
            return False

        return True

    def _validate_lines(self, file: str) -> bool:
        result = True

        with open(file) as reader:
            for line_number, line in enumerate(reader, 1):
                line = line.rstrip("\n")

                if not line.endswith("# dev-star ignore"):
                    result &= self._validate_character_limit(file, line, line_number)
                    result &= self._validate_zero_comparison(file, line, line_number)

        return result

    def _perform(self, all_files: bool = False, validate: bool = False) -> int:
        get_files_function = get_repo_files if all_files else get_changed_repo_files
        files = get_files_function([filter_python_files])
        write_back = WriteBack.NO if validate else WriteBack.YES
        output_stream = StringIO() if validate else None
        formatted = set()

        for file in files:
            try:
                if format_file_in_place(
                    Path(file), False, FileMode(), write_back
                ) | isort.file(file, output=output_stream, profile="black", quiet=True):
                    formatted.add(file)
            except InvalidInput:
                output(f"Cannot parse Python file '{file}'.")
                return ReturnCode.FAILED

            if not self._validate_lines(file) and validate:
                formatted.add(file)

        if len(formatted) > 0:
            if validate:
                output("The following files are misformatted:")
                for file in formatted:
                    output(f"  - {file}")

                return ReturnCode.FAILED

            output(
                f"Checked {len(files)} file{'s' if len(files) > 1 else ''} and "
                f"formatted {len(formatted)} file{'s' if len(formatted) > 1 else ''}."
            )

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")
        parser.add_argument("-v", "--validate", action="store_true", dest="validate")

        return parser
