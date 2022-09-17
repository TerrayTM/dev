import os
import re
import subprocess
from itertools import chain
from typing import Callable, List, Set, Tuple

GIT_ALL_FILES = ("git", "ls-files")
GIT_UNTRACKED_FILES = ("git", "ls-files", "--others", "--exclude-standard")
GIT_STAGED_FILES = ("git", "diff", "--name-only", "--cached", "--relative")
GIT_CHANGED_FILES = ("git", "diff", "--name-only", "--relative")
GIT_ROOT_DIRECTORY = ("git", "rev-parse", "--show-toplevel")


def _execute_git_commands(*commands: Tuple[str, ...]) -> List[str]:
    if not len(commands):
        raise ValueError()

    return list(
        chain.from_iterable(
            subprocess.check_output(command, encoding="utf-8").split("\n")
            for command in commands
        )
    )


def get_repo_files(
    filters: List[Callable[[str], bool]] = [], include_untracked: bool = True
) -> List[str]:
    comamnds = [GIT_ALL_FILES]

    if include_untracked:
        comamnds.append(GIT_UNTRACKED_FILES)

    return [
        os.path.abspath(path)
        for path in _execute_git_commands(*comamnds)
        if os.path.isfile(path)
        and all(filter_function(path) for filter_function in filters)
    ]


def get_changed_repo_files(filters: List[Callable[[str], bool]] = []) -> Set[str]:
    return set(
        os.path.abspath(path)
        for path in _execute_git_commands(
            GIT_CHANGED_FILES, GIT_STAGED_FILES, GIT_UNTRACKED_FILES
        )
        if os.path.isfile(path)
        and all(filter_function(path) for filter_function in filters)
    )


def get_repo_root_directory() -> str:
    return _execute_git_commands(GIT_ROOT_DIRECTORY)[0]


def filter_python_files(path: str) -> bool:
    return path.endswith(".py")


def filter_unit_test_files(path: str) -> bool:
    return os.path.basename(path).startswith("test_")


def filter_not_unit_test_files(path: str) -> bool:
    return not filter_unit_test_files(path)


def filter_not_cache_files(path: str) -> bool:
    return not "__pycache__" in path


def filter_not_python_underscore_files(path: str) -> bool:
    return not re.match(r"^.*__.*__\.py$", path)
