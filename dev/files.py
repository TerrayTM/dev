import os
import re
import subprocess
from functools import partial
from itertools import chain
from typing import Any, Callable, List, Optional, Set, Tuple

GIT_ALL_FILES = ("git", "ls-files")
GIT_UNTRACKED_FILES = ("git", "ls-files", "--others", "--exclude-standard")
GIT_STAGED_FILES = ("git", "diff", "--name-only", "--cached", "--relative")
GIT_CHANGED_FILES = ("git", "diff", "--name-only", "--relative")
GIT_ROOT_DIRECTORY = ("git", "rev-parse", "--show-toplevel")


def _execute_git_commands(*commands: Tuple[str, ...]) -> List[str]:
    if not commands:
        raise ValueError()

    return list(
        chain.from_iterable(
            subprocess.check_output(
                command, encoding="utf-8", stderr=subprocess.DEVNULL
            ).split("\n")
            for command in commands
        )
    )


def _execute_with_fallback(
    primary_function: Callable[[], Any], fallback_function: Callable[[], Any]
) -> Any:
    try:
        return primary_function()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return fallback_function()


def _native_get_all_files() -> List[str]:
    all_files: List[str] = []
    for current_path, directories, files in os.walk(os.getcwd()):
        directories[:] = [
            directory for directory in directories if not directory.startswith(".")
        ]
        all_files.extend(os.path.join(current_path, file) for file in files)

    return all_files


def evaluate_file_filters(
    filters: Optional[List[Callable[[str], bool]]], argument: str
) -> bool:
    if filters is None:
        return True

    return all(filter_function(argument) for filter_function in filters)


def get_repo_files(
    filters: Optional[List[Callable[[str], bool]]] = None,
    include_untracked: bool = True,
) -> Set[str]:
    commands: List[Tuple[str, ...]] = [GIT_ALL_FILES]

    if include_untracked:
        commands.append(GIT_UNTRACKED_FILES)

    return {
        os.path.abspath(path)
        for path in _execute_with_fallback(
            partial(_execute_git_commands, *commands), _native_get_all_files
        )
        if os.path.isfile(path) and evaluate_file_filters(filters, path)
    }


def get_changed_repo_files(
    filters: Optional[List[Callable[[str], bool]]] = None
) -> Set[str]:
    return {
        os.path.abspath(path)
        for path in _execute_with_fallback(
            partial(
                _execute_git_commands,
                GIT_CHANGED_FILES,
                GIT_STAGED_FILES,
                GIT_UNTRACKED_FILES,
            ),
            _native_get_all_files,
        )
        if os.path.isfile(path) and evaluate_file_filters(filters, path)
    }


def get_repo_root_directory() -> str:
    return _execute_with_fallback(
        partial(_execute_git_commands, GIT_ROOT_DIRECTORY), lambda: [os.getcwd()]
    )[0]


def paths_to_files(
    paths: List[str], filters: Optional[List[Callable[[str], bool]]] = None
) -> Set[str]:
    result: Set[str] = set()

    for path in paths:
        if os.path.isdir(path):
            for dirpath, _, files in os.walk(path):
                result.update(
                    os.path.abspath(os.path.join(dirpath, file))
                    for file in files
                    if evaluate_file_filters(filters, file)
                )
        elif os.path.isfile(path):
            if evaluate_file_filters(filters, path):
                result.add(os.path.abspath(path))
        else:
            raise FileNotFoundError(f"File '{path}' does not exist.")

    return result


def select_get_files_function(
    files: Optional[List[str]], all_files: bool
) -> Callable[[List[Callable[[str], bool]]], Set[str]]:
    if files and all_files:
        raise ValueError("Cannot specify files and set all files at the same time.")

    get_files_function = get_changed_repo_files
    if all_files:
        get_files_function = get_repo_files
    elif files:
        get_files_function = partial(paths_to_files, files)

    return get_files_function


def build_file_extensions_filter(extensions: Set[str]) -> Callable[[str], bool]:
    return lambda path: any(path.endswith(extension) for extension in extensions)


def filter_python_files(path: str) -> bool:
    return path.endswith(".py")


def filter_unit_test_files(path: str) -> bool:
    return os.path.basename(path).startswith("test_")


def filter_not_unit_test_files(path: str) -> bool:
    return not filter_unit_test_files(path)


def filter_not_cache_files(path: str) -> bool:
    return "__pycache__" not in path


def filter_not_python_underscore_files(path: str) -> bool:
    return not re.match(r"^.*__.*__\.py$", path)
