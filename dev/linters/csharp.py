from typing import Iterable, Set
from warnings import warn

from dev.linters.base import BaseLinter
from dev.linters.utils import (
    get_linter_program,
    two_phase_lint,
    validate_character_limit,
)

_LINTER_PREFIX = "Warning "
_LINTER_POSTFIX = " - Was not formatted."
_LINTER_ERROR_PREFIX = "Error "
_LINTER_ERROR_POSTFIX = " - Failed to compile so was not formatted."


class CSharpLinter(BaseLinter):
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
        if line_length != cls.get_width():
            warn("C# linter does not support setting line width.")

        generate_command = (
            lambda verify, target_files: [
                get_linter_program("dotnet-csharpier"),
                "--no-cache",
                "--fast",
            ]
            + (["--check"] if verify else [])
            + target_files
        )
        parse_error = (
            lambda line: line[len(_LINTER_ERROR_PREFIX) : -len(_LINTER_ERROR_POSTFIX)]
            if line.startswith(_LINTER_ERROR_PREFIX)
            else None
        )
        parse_formatted = (
            lambda line: line[len(_LINTER_PREFIX) : -len(_LINTER_POSTFIX)]
            if line.startswith(_LINTER_PREFIX)
            else None
        )

        return two_phase_lint(
            files, validate, generate_command, parse_error, parse_formatted
        )

    @staticmethod
    def get_install() -> str:
        return "dotnet tool install -g csharpier"

    @staticmethod
    def get_extension() -> str:
        return ".cs"

    @staticmethod
    def get_width() -> int:
        return 100
