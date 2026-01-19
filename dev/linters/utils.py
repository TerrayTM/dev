import shutil
import subprocess
from functools import partial
from typing import Callable, List, Optional, Set, Union

from dev.exceptions import LinterError, LinterNotInstalledError
from dev.output import output


def validate_character_limit(
    file: str, line: str, line_number: int, line_length: int
) -> bool:
    if len(line) > line_length:
        output(
            f"File '{file}' on line {line_number} exceeds the "
            f"width limit of {line_length} characters."
        )
        return False

    return True


def get_linter_program(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise LinterNotInstalledError()

    return path


def two_phase_lint(
    files: List[str],
    validate: bool,
    generate_command: Callable[[bool, List[str]], List[str]],
    parse_error: Callable[[str], Optional[Union[str, int]]],
    parse_formatted: Callable[[str], Optional[Union[str, int]]],
    error_output: str = "stderr",
    formatted_output: str = "stdout",
    expects_error: bool = False,
    ignores_error: bool = False,
) -> Set[str]:
    verify_result = None
    run_linter = partial(
        subprocess.run, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf8"
    )

    if not files:
        return set()

    verify_result = run_linter(generate_command(True, files))
    split_error_output = getattr(verify_result, error_output).split("\n")

    for index, line in enumerate(split_error_output):
        indicator = parse_error(line)

        if indicator is not None:
            path = (
                indicator
                if isinstance(indicator, str)
                else split_error_output[index + indicator]
            )

            raise LinterError(f"File '{path}' cannot be formatted.")

    formatted = set()
    split_standard_output = getattr(verify_result, formatted_output).split("\n")

    for index, line in enumerate(split_standard_output):
        indicator = parse_formatted(line)

        if indicator is not None:
            path = (
                indicator
                if isinstance(indicator, str)
                else split_standard_output[index + indicator]
            )

            formatted.add(path)

    if not validate and len(formatted) > 0:
        linter_result = run_linter(generate_command(False, list(formatted)))

        if not ignores_error and linter_result.returncode:
            error_message = (
                ""
                if expects_error
                else "A problem has occurred with the linter process."
            )

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
