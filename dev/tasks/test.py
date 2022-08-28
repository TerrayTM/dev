import subprocess
from argparse import ArgumentParser, Namespace, _SubParsersAction
from pathlib import Path
from time import time

from tqdm.contrib.concurrent import thread_map

from dev.constants import RC_FAILED, RC_OK
from dev.tasks.task import Task

CONSOLE_RED = "\033[91m"
CONSOLE_END_COLOR = "\033[0m"


class TestTask(Task):
    def _perform(self, args: Namespace) -> int:
        if args.use_loader:
            result = subprocess.run(["python", "-m", "unittest", "discover"])
            return RC_OK if not result.returncode else RC_FAILED

        rc = RC_OK
        start_time = time()
        tests = list(
            path
            for path in Path(".").rglob("test_*.py")
            if not "__pycache__" in str(path)
        )

        if not len(tests):
            print("No test suites found.")
            return RC_OK

        results = thread_map(
            lambda test: (
                subprocess.run(
                    ["python", "-m", str(test).replace("\\", ".")[:-3]],
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
            if process_result.returncode:
                print(f"{CONSOLE_RED}{test}{CONSOLE_END_COLOR}")
                print("*" * 70)
                print(process_result.stdout)
                rc = RC_FAILED

        if rc == RC_OK:
            print(
                f"[OK] Ran {len(tests)} test suites in "
                f"{round(time() - start_time, 3)}s."
            )

        return rc

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("--use-loader", action="store_true", dest="use_loader")

        return parser
