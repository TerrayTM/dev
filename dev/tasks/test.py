import os
import subprocess
from argparse import ArgumentParser, _SubParsersAction
from typing import List

from tqdm.contrib.concurrent import thread_map

from dev.constants import ReturnCode
from dev.files import (
    filter_not_cache_files,
    filter_python_files,
    filter_unit_test_files,
    get_repo_files,
    get_repo_root_directory,
)
from dev.output import ConsoleColors, output
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
        )

        for process_result, test in results:
            if not process_result.stdout:
                output(f"Test suite '{test}' failed to execute.")
                rc = ReturnCode.FAILED
            elif process_result.returncode:
                output(ConsoleColors.RED, test, ConsoleColors.END)
                output("*" * 70)
                output(process_result.stdout)
                rc = ReturnCode.FAILED

        return rc

    def _perform(self, use_loader: bool = False) -> int:
        if use_loader:
            result = subprocess.run(["python", "-m", "unittest", "discover"])
            return ReturnCode.OK if not result.returncode else ReturnCode.FAILED

        root_directory = get_repo_root_directory()
        tests = get_repo_files(
            [filter_python_files, filter_unit_test_files, filter_not_cache_files]
        )

        if not len(tests):
            output("No test suites found.")
            return ReturnCode.OK

        result = measure_time(
            self._run_tests, root_directory, tests, raise_exception=True
        )

        if result.return_value == ReturnCode.OK:
            output(f"[OK] Ran {len(tests)} test suites in {round(result.elasped, 3)}s.")

        return result.return_value

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-u", "--use-loader", action="store_true", dest="use_loader"
        )

        return parser
