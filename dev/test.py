import subprocess
from argparse import Namespace
from pathlib import Path
from time import time

from dev.constants import RC_OK
from dev.task import Task


class TestTask(Task):
    def _perform(self, _: Namespace) -> int:
        tests = list(Path(".").rglob("test_*.py"))
        start_time = time()

        for test in tests:
            result = subprocess.run(
                ["python", "-m", str(test).replace("\\", ".").rstrip(".py")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding="utf8",
            )

            if result.returncode:
                print(test)
                print(result.stdout)
                break
        else:
            print(
                f"[OK] Ran {len(tests)} test suites in {round(time() - start_time, 3)}s"
            )

        return RC_OK
