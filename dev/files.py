import os
import re
import subprocess
from typing import Callable, List, Tuple

GIT_ALL_FILES = ("git", "ls-files")
GIT_UNTRACKED_FILES = ("git", "ls-files", "--others", "--exclude-standard")
GIT_STAGED_FILES = ("git", "diff", "--name-only", "--cached")
GIT_CHANGED_FILES = ("git", "diff", "--name-only")


def _execute_git_command(command: Tuple[str, ...]) -> List[str]:
    return subprocess.check_output(command, encoding="utf-8").split("\n")


def get_repo_files(filters: List[Callable[[str], bool]] = []) -> List[str]:
    return [
        os.path.abspath(path)
        for path in _execute_git_command(GIT_ALL_FILES)
        if os.path.isfile(path)
        and all(filter_function(path) for filter_function in filters)
    ]


def get_changed_repo_files(filters: List[Callable[[str], bool]] = []) -> List[str]:
    return [
        os.path.abspath(path)
        for path in _execute_git_command(GIT_CHANGED_FILES)
        + _execute_git_command(GIT_STAGED_FILES)
        + _execute_git_command(GIT_UNTRACKED_FILES)
        if os.path.isfile(path)
        and all(filter_function(path) for filter_function in filters)
    ]


def filter_python_files(path: str) -> bool:
    return path.endswith(".py")


def filter_not_python_unit_test_files(path: str) -> bool:
    return not os.path.basename(path).startswith("test_")


def filter_not_python_underscore_files(path: str) -> bool:
    return not re.match("^.*__.*__\.py$", path)
