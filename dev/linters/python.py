import re
import subprocess
from typing import List, Set

from dev.exceptions import LinterError
from dev.linters.base import BaseLinter
from dev.linters.utils import validate_character_limit
from dev.output import output

_FORMAT_PATTERN = re.compile(r"^Would reformat: (.+)$")
_CHECK_PATTERN = re.compile(r"^(.+?):\d+:\d+:")


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
    def _validate_bad_default_arguments(file: str, line: str, line_number: int) -> bool:
        if any(
            search in line
            for search in [
                "= [],",  # dev-star ignore
                "= [])",  # dev-star ignore
                "= {},",  # dev-star ignore
                "= {})",  # dev-star ignore
                "= set(),",  # dev-star ignore
                "= set())",  # dev-star ignore
            ]
        ):
            output(
                f"File '{file}' on line {line_number} is using a bad default argument."
            )
            return False

        return True

    @staticmethod
    def _validate_comma_bracket_ending(file: str, line: str, line_number: int) -> bool:
        if ",)" in line or ",]" in line:  # dev-star ignore
            output(
                f"File '{file}' on line {line_number} is using a comma bracket ending."
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
            & cls._validate_bad_default_arguments(file, line, line_number)
            & cls._validate_comma_bracket_ending(file, line, line_number)
        )

    @classmethod
    def _format(cls, files: List[str], line_length: int, validate: bool) -> Set[str]:
        line_length_str = str(line_length)

        format_result = subprocess.run(
            [
                "ruff",
                "format",
                "--check",
                "--line-length",
                line_length_str,
                "--config",
                "format.skip-magic-trailing-comma = true",
            ]
            + files,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        )
        if format_result.returncode > 1:
            raise LinterError(format_result.stderr.strip())

        check_result = subprocess.run(
            ["ruff", "check", "--select", "I", "--line-length", line_length_str]
            + files,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf8",
        )
        if check_result.returncode > 1:
            raise LinterError(check_result.stderr.strip())

        formatted = set()

        for line in (format_result.stdout + format_result.stderr).splitlines():
            if match := _FORMAT_PATTERN.match(line.strip()):
                formatted.add(match.group(1))

        for line in check_result.stdout.splitlines():
            if match := _CHECK_PATTERN.match(line):
                formatted.add(match.group(1))

        if not validate:
            subprocess.run(
                [
                    "ruff",
                    "check",
                    "--select",
                    "I",
                    "--fix",
                    "--line-length",
                    line_length_str,
                ]
                + files,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            subprocess.run(
                [
                    "ruff",
                    "format",
                    "--line-length",
                    line_length_str,
                    "--config",
                    "format.skip-magic-trailing-comma = true",
                ]
                + files,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        return formatted

    @staticmethod
    def get_install() -> str:
        return "pip install ruff"

    @staticmethod
    def get_extensions() -> List[str]:
        return [".py"]

    @staticmethod
    def get_width() -> int:
        return 88
