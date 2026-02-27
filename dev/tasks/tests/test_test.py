from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.test import TestTask


def _make_process_result(stdout: str, returncode: int = 0) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.returncode = returncode
    return result


class TestTestTask(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream
        self._task = TestTask()

    def test_run_tests_success(self) -> None:
        result = _make_process_result("Ran 3 tests in 0.001s\n\nOK\n")
        with patch(
            "dev.tasks.test.thread_map",
            return_value=[(result, "/root/test_foo.py")],
        ):
            rc = self._task._run_tests("/root", ["/root/test_foo.py"])

        self.assertEqual(rc, ReturnCode.OK)

    def test_run_tests_failure(self) -> None:
        result = _make_process_result("FAIL: test_x\n\nRan 1 test\n", returncode=1)
        with patch(
            "dev.tasks.test.thread_map",
            return_value=[(result, "/root/test_foo.py")],
        ):
            rc = self._task._run_tests("/root", ["/root/test_foo.py"])

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_run_tests_no_output_fails(self) -> None:
        result = _make_process_result("")
        with patch(
            "dev.tasks.test.thread_map",
            return_value=[(result, "/root/test_foo.py")],
        ):
            rc = self._task._run_tests("/root", ["/root/test_foo.py"])

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_run_tests_missing_ran_line_fails(self) -> None:
        result = _make_process_result("some output without the ran line\n")
        with patch(
            "dev.tasks.test.thread_map",
            return_value=[(result, "/root/test_foo.py")],
        ):
            rc = self._task._run_tests("/root", ["/root/test_foo.py"])

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_perform_no_test_files_returns_ok(self) -> None:
        with patch("dev.tasks.test.get_repo_files", return_value=set()):
            rc = TestTask.execute()

        self.assertEqual(rc, ReturnCode.OK)
        self.assertIn("No test suites found", self._stream.getvalue())

    def test_perform_match_filters_tests(self) -> None:
        all_tests = {"/root/test_foo.py", "/root/test_bar.py"}
        with patch("dev.tasks.test.get_repo_files", return_value=all_tests), patch(
            "dev.tasks.test.get_repo_root_directory", return_value="/root"
        ), patch.object(TestTask, "_run_tests", return_value=ReturnCode.OK) as mock_run:
            TestTask.execute(match="test_foo")

        _, called_tests = mock_run.call_args[0]
        self.assertEqual(len(called_tests), 1)
        self.assertTrue(next(iter(called_tests)).endswith("test_foo.py"))


if __name__ == "__main__":
    main()
