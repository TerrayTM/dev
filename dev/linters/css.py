import tempfile
from functools import partial
from typing import Iterable, List, Set
from warnings import warn

from dev.linters.base import BaseLinter
from dev.linters.utils import (
    get_linter_program,
    two_phase_lint,
    validate_character_limit,
)

_LINTER_CONFIG = """{
  "extends": "stylelint-config-standard",
  "rules": {
    "selector-class-pattern": null,
    "no-descending-specificity": null,
    "selector-id-pattern": null
  }
}
"""


class CSSLinter(BaseLinter):
    @staticmethod
    def _get_comment() -> str:
        return "/*"

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
            warn("CSS linter does not support setting line width.")

        generate_command = (
            lambda config_path, verify, target_files: [
                get_linter_program("stylelint"),
                "--config",
                config_path,
            ]
            + ([] if verify else ["--fix"])
            + target_files
        )
        parse_error = lambda line: -1 if "CssSyntaxError" in line else None
        parse_formatted = lambda line: line if ".css" in line else None

        with tempfile.TemporaryFile(mode="wt", suffix=".json") as config_file:
            config_file.write(_LINTER_CONFIG)
            config_file.flush()

            return two_phase_lint(
                files,
                validate,
                partial(generate_command, config_file.name),
                parse_error,
                parse_formatted,
                "stdout",
                expects_error=True,
            )

    @staticmethod
    def get_install() -> str:
        return "npm install -g stylelint stylelint-config-standard"

    @staticmethod
    def get_extensions() -> List[str]:
        return [".css"]

    @staticmethod
    def get_width() -> int:
        return 100
