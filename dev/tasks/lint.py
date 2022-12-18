from argparse import ArgumentParser, _SubParsersAction
from io import StringIO
from pathlib import Path
from typing import List

import isort
from black import FileMode, InvalidInput, WriteBack, format_file_in_place

from dev.constants import ReturnCode
from dev.files import filter_python_files, select_get_files_function
from dev.output import output
from dev.tasks.task import Task

DEFAULT_LINE_LENGTH = 88


class LintTask(Task):
    def _validate_character_limit(
        self, line_length: int, file: str, line: str, line_number: int
    ) -> bool:
        if len(line) > line_length:
            output(
                f"File '{file}' on line {line_number} exceeds the "
                f"width limit of {line_length} characters."
            )
            return False

        return True

    def _validate_zero_comparison(self, file: str, line: str, line_number: int) -> bool:
        if "== 0" in line or "!= 0" in line:  # dev-star ignore
            output(f"File '{file}' on line {line_number} is comparing to zero.")
            return False

        return True

    def _validate_lines(self, line_length: int, file: str) -> bool:
        result = True

        with open(file) as reader:
            for line_number, line in enumerate(reader, 1):
                line = line.rstrip("\n")

                if not line.endswith("# dev-star ignore"):
                    result &= self._validate_character_limit(
                        line_length, file, line, line_number
                    )
                    result &= self._validate_zero_comparison(file, line, line_number)

        return result

    def _plural(self, count: int) -> str:
        return "" if count == 1 else "s"

    def _perform(
        self,
        files: List[str] = [],
        all_files: bool = False,
        validate: bool = False,
        line_length: int = DEFAULT_LINE_LENGTH,
    ) -> int:
        target_files = None
        try:
            target_files = select_get_files_function(files, all_files)(
                [filter_python_files]
            )
        except Exception as error:
            output(str(error))
            return ReturnCode.FAILED

        write_back = WriteBack.NO if validate else WriteBack.YES
        output_stream = StringIO() if validate else None
        formatted = set()
        mode = FileMode()
        mode.line_length = line_length

        for file in target_files:
            try:
                if format_file_in_place(
                    Path(file), False, mode, write_back
                ) | isort.file(
                    file,
                    output=output_stream,
                    profile="black",
                    quiet=True,
                    line_length=line_length,
                ):
                    formatted.add(file)
            except InvalidInput:
                output(f"Cannot parse Python file '{file}'.")
                return ReturnCode.FAILED

            if not self._validate_lines(line_length, file) and validate:
                formatted.add(file)

        if len(formatted) > 0:
            if validate:
                output("The following files are misformatted:")
                for file in formatted:
                    output(f"  - {file}")

                return ReturnCode.FAILED

            output(
                f"Checked {len(target_files)} file{self._plural(len(target_files))} "
                f"formatted {len(formatted)} file{self._plural(len(formatted))}."
            )

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("files", nargs="*")
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")
        parser.add_argument("-v", "--validate", action="store_true", dest="validate")
        parser.add_argument(
            "-l",
            "--line-length",
            type=int,
            dest="line_length",
            default=DEFAULT_LINE_LENGTH,
        )

        return parser
