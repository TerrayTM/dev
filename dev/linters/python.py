from io import StringIO
from pathlib import Path
from typing import Iterable, Set

import isort
from black import FileMode, InvalidInput, WriteBack, format_file_in_place

from dev.exceptions import LinterError
from dev.linters.base import BaseLinter
from dev.linters.utils import validate_character_limit
from dev.output import output


class PythonLinter(BaseLinter):
    @staticmethod
    def _get_comment() -> str:
        return "#"

    @staticmethod
    def _validate_zero_comparison(file: str, line: str, line_number: int) -> bool:
        if "== 0" in line or "!= 0" in line:  # dev-star ignore
            output(f"File '{file}' on line {line_number} is comparing to zero.")
            return False

        return True

    @staticmethod
    def _validate_set_construction(file: str, line: str, line_number: int) -> bool:
        if "set([" in line:  # dev-star ignore
            output(f"File '{file}' on line {line_number} is constructing a set.")
            return False

        return True

    @staticmethod
    def _validate_not_in_order(file: str, line: str, line_number: int) -> bool:
        if " not " in line and " in " in line and "not in" not in line:
            output(
                f"File '{file}' on line {line_number} "
                "is using an incorrect 'not in' order."
            )
            return False

        return True

    @staticmethod
    def _validate_bad_default_arguments(file: str, line: str, line_number: int) -> bool:
        if any(
            search in line
            for search in ["= [],", "= [])", "= {},", "= {})"]  # dev-star ignore
        ):
            output(
                f"File '{file}' on line {line_number} is using a bad default argument."
            )
            return False

        return True

    @classmethod
    def _validate(
        cls, file: str, line_length: int, line: str, line_number: int
    ) -> bool:
        return (
            validate_character_limit(file, line, line_number, line_length)
            & cls._validate_zero_comparison(file, line, line_number)
            & cls._validate_set_construction(file, line, line_number)
            & cls._validate_not_in_order(file, line, line_number)
            & cls._validate_bad_default_arguments(file, line, line_number)
        )

    @classmethod
    def _format(
        cls, files: Iterable[str], line_length: int, validate: bool
    ) -> Set[str]:
        write_back = WriteBack.NO if validate else WriteBack.YES
        output_stream = StringIO() if validate else None
        mode = FileMode()
        mode.line_length = line_length
        formatted = set()

        for file in files:
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
                raise LinterError(f"Cannot format Python file '{file}'.")

        return formatted

    @staticmethod
    def get_extension() -> str:
        return ".py"

    @staticmethod
    def get_width() -> int:
        return 88
