import subprocess
from typing import Iterable, Set
from warnings import warn

from dev.exceptions import LinterError
from dev.linters.base import BaseLinter
from dev.linters.utils import validate_character_limit

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

        run_linter = lambda verify, targeted_files: subprocess.run(
            ["dotnet-csharpier", "--no-cache", "--fast"]
            + (["--check"] if verify else [])
            + targeted_files,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        )

        selected_files = list(files)
        if not selected_files:
            return set()

        verify_result = run_linter(True, selected_files)
        for file in verify_result.stderr.split("\n"):
            if file.startswith(_LINTER_ERROR_PREFIX):
                raise LinterError(
                    "Cannot format C# file "
                    f"{file[len(_LINTER_ERROR_PREFIX) : -len(_LINTER_ERROR_POSTFIX)]}'."
                )

        formatted = {
            file[len(_LINTER_PREFIX) : -len(_LINTER_POSTFIX)]
            for file in verify_result.stdout.split("\n")
            if file.startswith(_LINTER_PREFIX)
        }

        if not validate and len(formatted) > 0:
            linter_result = run_linter(False, list(formatted))

            if linter_result.returncode:
                error_message = "A problem has occurred with the linter process."

                if linter_result.stdout:
                    error_message += (
                        f"\nLinter standard output:\n{'='*70}\n{linter_result.stdout}"
                    )
                if linter_result.stderr:
                    error_message += (
                        f"\nLinter error output:\n{'='*70}\n{linter_result.stderr}"
                    )

                raise LinterError(error_message)

        return formatted

    @staticmethod
    def get_extension() -> str:
        return ".cs"

    @staticmethod
    def get_width() -> int:
        return 100
