import os
import subprocess
from io import StringIO
from unittest import TestCase, main

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.process import run_process


class TestProcess(TestCase):
    def test_run_process(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        rc = run_process(["echo", "123"], shell=True).returncode

        self.assertEqual(stream.getvalue(), "123\n")
        self.assertEqual(rc, ReturnCode.OK)

    def test_environment(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        run_process(
            ["python", "-c", 'import os; print(os.environ["TEST"])'],
            shell=True,
            env={**os.environ, "TEST": "123"},
        )

        self.assertEqual(stream.getvalue(), "123\n")

    def test_check_call(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        with self.assertRaises(subprocess.CalledProcessError):
            run_process(
                ["python", "-c", "raise SystemExit(6)"], check_call=True, shell=True
            )


if __name__ == "__main__":
    main()
