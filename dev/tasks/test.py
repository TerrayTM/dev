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


class TestTask(Task):
    def _run_tests(self, root_directory: str, tests: List[str]) -> int:
        rc = ReturnCode.OK
        results = thread_map(
            lambda test: (
                subprocess.run(
                    [
                        "python",
                        "-m",
                        os.path.relpath(test, root_directory).replace("\\", ".")[:-3],
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    encoding="utf8",
                ),
                test,
            ),
            tests,
            desc="Testing",
            leave=False,
            unit="suite",
            disable=not is_using_stdout(),
        )

        for process_result, test in results:
            relative_test = os.path.relpath(test, os.getcwd())

            if not process_result.stdout:
                output(
                    ConsoleColors.RED,
                    f"Test suite '{relative_test}' failed to execute.",
                    ConsoleColors.END,
                )
                rc = ReturnCode.FAILED
            elif process_result.returncode:
                output(ConsoleColors.RED, relative_test, ConsoleColors.END)
                output("*" * 70)
                output(process_result.stdout)
                output("*" * 70)
                rc = ReturnCode.FAILED
            else:
                for line in process_result.stdout.split("\n"):
                    if line.startswith("Ran"):
                        output(f"{line}: {relative_test}")
                        break
                else:
                    raise RuntimeError("Cannot determine how many tests were ran.")

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
            tests = [path for path in tests if match in path]

        if not len(tests):
            output("No test suites found.")
            return ReturnCode.OK

        result = measure_time(
            self._run_tests, root_directory, tests, raise_exception=True
        )

        if result.return_value == ReturnCode.OK:
            output(f"[OK] Ran {len(tests)} test suites in {round(result.elapsed, 3)}s.")

        return result.return_value

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-u", "--use-loader", action="store_true", dest="use_loader"
        )
        parser.add_argument("-m", "--match", dest="match")
        return parser
