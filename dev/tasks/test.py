import os
import subprocess
from argparse import ArgumentParser, _SubParsersAction
from typing import List, Optional

from tqdm.contrib.concurrent import thread_map

from dev.constants import ReturnCode
from dev.files import (
    filter_not_cache_files,
    filter_python_files,
    filter_unit_test_files,
    get_repo_files,
    get_repo_root_directory,
)
from dev.output import ConsoleColors, is_using_stdout, output
from dev.process import run_process
from dev.tasks.task import Task
from dev.timer import measure_time


def _write_error_output(path: str, content: str) -> None:
    output(ConsoleColors.RED, path, ConsoleColors.END)
    output("*" * 70)
    output(content)
    output("*" * 70)


class TestTask(Task):
    def _run_tests(self, root_directory: str, tests: List[str]) -> int:
        rc = ReturnCode.OK
        results = thread_map(
            lambda test_path: (
                subprocess.run(
                    [
                        "python",
                        "-m",
                        os.path.relpath(test_path, root_directory).replace("\\", ".")[
                            :-3
                        ],
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                ),
                test_path,
            ),
            tests,
            desc="Testing",
            leave=False,
            unit="suite",
            disable=not is_using_stdout(),
        )

        for process_result, test_path in sorted(results, key=lambda entry: entry[-1]):
            relative_test_path = os.path.relpath(test_path, os.getcwd())

            try:
                stdout = (
                    process_result.stdout.decode("utf8")
                    if process_result.stdout
                    else ""
                )
            except UnicodeDecodeError as exception:
                output(
                    ConsoleColors.RED,
                    f"Test suite '{relative_test_path}' produced output that could not "
                    f"be decoded as UTF-8: {exception}",
                    ConsoleColors.END,
                )
                rc = ReturnCode.FAILED
                continue

            if not stdout:
                output(
                    ConsoleColors.RED,
                    f"Test suite '{relative_test_path}' failed to execute.",
                    ConsoleColors.END,
                )
                rc = ReturnCode.FAILED
            elif process_result.returncode:
                _write_error_output(relative_test_path, stdout)
                rc = ReturnCode.FAILED
            else:
                for line in stdout.splitlines():
                    if line.startswith("Ran"):
                        output(f"{line}: {relative_test_path}")
                        break
                else:
                    _write_error_output(relative_test_path, process_result.stdout)
                    rc = ReturnCode.FAILED

        return rc

    def _perform(self, use_loader: bool = False, match: Optional[str] = None) -> int:
        if use_loader:
            result = run_process(["python", "-m", "unittest", "discover"])
            return ReturnCode.OK if not result.returncode else ReturnCode.FAILED

        root_directory = get_repo_root_directory()
        tests = get_repo_files(
            [filter_python_files, filter_unit_test_files, filter_not_cache_files]
        )

        if match is not None:
            tests = {path for path in tests if match in path}

        if not len(tests):
            output("No test suites found.")
            return ReturnCode.OK

        timer_result = measure_time(
            self._run_tests, root_directory, tests, raise_exception=True
        )

        label = "OK" if timer_result.return_value == ReturnCode.OK else "FAILED"
        output(
            f"[{label}] Ran {len(tests)} test suites in "
            f"{round(timer_result.elapsed, 3)}s."
        )

        return timer_result.return_value

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-u", "--use-loader", action="store_true", dest="use_loader"
        )
        parser.add_argument("-m", "--match", dest="match")
        return parser
