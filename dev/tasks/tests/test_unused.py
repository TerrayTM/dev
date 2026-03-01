from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.unused import UnusedTask


class TestUnused(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_no_files_returns_ok(self) -> None:
        with patch(
            "dev.tasks.unused.select_get_files_function", return_value=lambda _: set()
        ):
            rc = UnusedTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_no_unused_imports_returns_ok(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = "no issues found\n"
        with patch(
            "dev.tasks.unused.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.unused.subprocess.run", return_value=mock_result):
            rc = UnusedTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_unused_import_returns_failed(self) -> None:
        mock_result = MagicMock()
        mock_result.stdout = "file.py:1:0: W0611: Unused import os (unused-import)\n"
        with patch(
            "dev.tasks.unused.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.unused.subprocess.run", return_value=mock_result):
            rc = UnusedTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)
        self.assertIn("W0611", self._stream.getvalue())


if __name__ == "__main__":
    main()
