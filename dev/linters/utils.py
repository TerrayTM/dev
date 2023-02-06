import subprocess
from functools import partial
from typing import Callable, Iterable, List, Optional, Set

from dev.exceptions import LinterError
from dev.output import output


def validate_character_limit(
    file: str, line: str, line_number: int, line_length: int,
) -> bool:
    if len(line) > line_length:
        output(
            f"File '{file}' on line {line_number} exceeds the "
            f"width limit of {line_length} characters."
        )
        return False

    return True


def two_phase_lint(
    files: Iterable[str],
    validate: bool,
    generate_command: Callable[[bool, List[str]], List[str]],
    parse_error: Callable[[str], Optional[str]],
    parse_formatted: Callable[[str], Optional[str]],
    error_output: str = "stderr",
    formatted_output: str = "stdout",
) -> Set[str]:
    run_linter = partial(
        subprocess.run,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf8",
    )

    selected_files = list(files)
    if not selected_files:
        return set()

    verify_result = run_linter(generate_command(True, selected_files))

    for line in getattr(verify_result, error_output).split("\n"):
        path = parse_error(line)
        if path is not None:
            raise LinterError(f"File '{path}' cannot be formatted.")

    formatted = set()
    for line in getattr(verify_result, formatted_output).split("\n"):
        path = parse_formatted(line)
        if path is not None:
            formatted.add(path)

    if not validate and len(formatted) > 0:
        linter_result = run_linter(generate_command(False, list(formatted)))

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
