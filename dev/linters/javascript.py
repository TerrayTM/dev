import subprocess
from typing import Iterable, Set

from dev.exceptions import LinterError
from dev.linters.base import BaseLinter
from dev.linters.utils import validate_character_limit


class JavascriptLinter(BaseLinter):
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
        targeted_files = list(files)
        run_linter = lambda flag: subprocess.run(
            [
                "prettier",
                flag,
                "--single-quote",
                "--print-width",
                str(line_length),
            ]
            + targeted_files,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding="utf8",
        )

        if not targeted_files:
            return set()

        formatted = set(
            file
            for file in run_linter("--list-different").stdout.split("\n")
            if len(file) > 0
        )

        if not validate and run_linter("--write").returncode:
            raise LinterError("A problem has occurred with the linter process.")

        return formatted

    @staticmethod
    def get_extension() -> str:
        return ".js"

    @staticmethod
    def get_width() -> int:
        return 80
