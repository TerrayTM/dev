from pathlib import Path
from typing import Iterable, List, Set

from dev.linters.base import BaseLinter
from dev.linters.utils import (
    get_linter_program,
    two_phase_lint,
    validate_character_limit,
)

_LINTER_ERROR_PREFIX = "[error] "


class JavaScriptLinter(BaseLinter):
    @staticmethod
    def _get_comment() -> str:
        return "//"

    @classmethod
    def _validate(
        cls, file: str, line_length: int, line: str, line_number: int
    ) -> bool:
        return validate_character_limit(file, line, line_number, line_length)

    @classmethod
    def _format(
        cls, files: Iterable[str], line_length: int, validate: bool
    ) -> Set[str]:
        generate_command = (
            lambda verify, target_files: [
                get_linter_program("prettier"),
                "--list-different" if verify else "--write",
                "--single-quote",
                "--print-width",
                str(line_length),
            ]
            + target_files
        )
        parse_error = (
            lambda line: line[len(_LINTER_ERROR_PREFIX) :].split(":")[0]
            if line.startswith(_LINTER_ERROR_PREFIX)
            else None
        )
        parse_formatted = (
            lambda line: str(Path(line).resolve()) if len(line) > 0 else None
        )

        return two_phase_lint(
            files, validate, generate_command, parse_error, parse_formatted
        )

    @staticmethod
    def get_install() -> str:
        return "npm install -g prettier"

    @staticmethod
    def get_extensions() -> List[str]:
        return [".js"]

    @staticmethod
    def get_width() -> int:
        return 80
