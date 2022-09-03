import os
import subprocess
from argparse import ArgumentParser, _SubParsersAction
from time import time

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


class TestTask(Task):
    def _perform(self, use_loader: bool = False) -> int:
        if use_loader:
            result = subprocess.run(["python", "-m", "unittest", "discover"])
            return ReturnCode.OK if not result.returncode else ReturnCode.FAILED

        rc = ReturnCode.OK
        start_time = time()
        root_directory = get_repo_root_directory()
        tests = get_repo_files(
            [filter_python_files, filter_unit_test_files, filter_not_cache_files]
        )

        if not len(tests):
            output("No test suites found.")
            return ReturnCode.OK

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

        if rc == ReturnCode.OK:
            output(
                f"[OK] Ran {len(tests)} test suites in "
                f"{round(time() - start_time, 3)}s."
            )

        return rc

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument(
            "-u", "--use-loader", action="store_true", dest="use_loader"
        )

        return parser
