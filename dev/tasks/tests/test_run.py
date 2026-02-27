import os
import tempfile
from argparse import Namespace
from io import StringIO
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.run import RunTask


class TestRun(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream
        self._original_dir = os.getcwd()
        self._temp_dir = tempfile.mkdtemp()
        os.chdir(self._temp_dir)

    def tearDown(self) -> None:
        os.chdir(self._original_dir)

    def test_single_main_py_runs_program(self) -> None:
        (Path(self._temp_dir) / "main.py").touch()

        with patch("dev.tasks.run.run_process") as mock_run:
            rc = RunTask.execute()

        mock_run.assert_called_once()
        self.assertEqual(rc, ReturnCode.OK)

    def test_no_main_py_outputs_error(self) -> None:
        with patch("dev.tasks.run.run_process") as mock_run:
            rc = RunTask.execute()

        mock_run.assert_not_called()
        self.assertIn("Cannot automatically determine", self._stream.getvalue())
        self.assertEqual(rc, ReturnCode.OK)

    def test_multiple_main_py_outputs_error(self) -> None:
        (Path(self._temp_dir) / "main.py").touch()
        sub = Path(self._temp_dir) / "sub"
        sub.mkdir()
        (sub / "main.py").touch()

        with patch("dev.tasks.run.run_process") as mock_run:
            rc = RunTask.execute()

        mock_run.assert_not_called()
        self.assertIn("Cannot automatically determine", self._stream.getvalue())
        self.assertEqual(rc, ReturnCode.OK)

    def test_passes_args_to_program(self) -> None:
        (Path(self._temp_dir) / "main.py").touch()

        with patch("dev.tasks.run.run_process") as mock_run:
            RunTask.execute(args=Namespace(args=["--flag", "value"]))

        called_args = mock_run.call_args[0][0]
        self.assertIn("--flag", called_args)
        self.assertIn("value", called_args)


if __name__ == "__main__":
    main()
