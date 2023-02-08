import os
import re
import tempfile
from functools import partial
from typing import Iterable, Set
from warnings import warn

from dev.linters.base import BaseLinter
from dev.linters.utils import two_phase_lint, validate_character_limit

_LINTER_CONFIG = """<?php
$config = new PhpCsFixer\Config();
$config->setRules(['@PhpCsFixer' => true])->setUsingCache(false);
return $config;
"""


class PHPLinter(BaseLinter):
    @staticmethod
    def _get_comment() -> str:
        return "#"

    @classmethod
    def _validate(
        cls, file: int, line_length: int, line: str, line_number: int
    ) -> bool:
        return validate_character_limit(file, line, line_number, line_length)

    @classmethod
    def _format(
        cls, files: Iterable[str], line_length: int, validate: bool
    ) -> Set[str]:
        if line_length != cls.get_width():
            warn("PHP linter does not support setting line width.")

        cwd_parent = os.path.dirname(os.getcwd())
        generate_command = (
            lambda config_path, verify, target_files: [
                "composer",
                "global",
                "exec",
                "--",
                "php-cs-fixer",
                "fix",
                "--config=" + config_path.replace("\\", "\\\\"),
            ]
            + (["--dry-run"] if verify else [])
            + list(target_file.replace("\\", "\\\\") for target_file in target_files)
        )
        parse_path = (
            lambda line: ") ".join(line.split(") ")[1:])
            if re.match(r"\s+[0-9]+\) ", line)
            else None
        )

        def parse_formatted(line):
            result = parse_path(line)
            return os.path.join(cwd_parent, result) if result is not None else None

        with tempfile.TemporaryFile(mode="wt", suffix=".php") as config_file:
            config_file.write(_LINTER_CONFIG)
            config_file.flush()

            return two_phase_lint(
                files,
                validate,
                partial(generate_command, config_file.name),
                parse_path,
                parse_formatted,
            )

    @staticmethod
    def get_install() -> str:
        return "composer global require friendsofphp/php-cs-fixer"

    @staticmethod
    def get_extension() -> str:
        return ".php"

    @staticmethod
    def get_width() -> int:
        return 88
