from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.time import TimeTask


class TestTime(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_zero_count_fails(self) -> None:
        rc = TimeTask.execute(command=["echo"], count=0)
        self.assertEqual(rc, ReturnCode.FAILED)

    def test_negative_count_fails(self) -> None:
        rc = TimeTask.execute(command=["echo"], count=-1)
        self.assertEqual(rc, ReturnCode.FAILED)

    def test_runs_command_once(self) -> None:
        with patch(
            "dev.tasks.time.subprocess.run", return_value=MagicMock()
        ) as mock_run:
            rc = TimeTask.execute(command=["echo", "hi"], count=1)

        self.assertEqual(mock_run.call_count, 1)
        self.assertEqual(rc, ReturnCode.OK)

    def test_runs_command_multiple_times(self) -> None:
        with patch(
            "dev.tasks.time.subprocess.run", return_value=MagicMock()
        ) as mock_run:
            rc = TimeTask.execute(command=["echo"], count=3)

        self.assertEqual(mock_run.call_count, 3)
        self.assertEqual(rc, ReturnCode.OK)

    def test_output_reports_best_time(self) -> None:
        with patch("dev.tasks.time.subprocess.run", return_value=MagicMock()):
            TimeTask.execute(command=["echo"], count=2)

        self.assertIn("Best of 2 trials", self._stream.getvalue())


if __name__ == "__main__":
    main()
