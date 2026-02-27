from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.exceptions import LinterError, LinterNotInstalledError
from dev.output import OutputConfig
from dev.tasks.lint import LintTask


def _make_mock_linter(formatted: set) -> MagicMock:
    linter = MagicMock()
    linter.get_extensions.return_value = [".py"]
    linter.get_width.return_value = 88
    linter.format.return_value = formatted
    return linter


class TestLint(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_no_files_returns_ok(self) -> None:
        with patch(
            "dev.tasks.lint.select_get_files_function",
            return_value=lambda _: set(),
        ):
            rc = LintTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_files_with_no_changes_returns_ok(self) -> None:
        mock_linter = _make_mock_linter(set())
        with patch(
            "dev.tasks.lint.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.lint._INSTALLED_LINTERS", [mock_linter]):
            rc = LintTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_validate_mode_with_formatted_files_fails(self) -> None:
        mock_linter = _make_mock_linter({"file.py"})
        with patch(
            "dev.tasks.lint.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.lint._INSTALLED_LINTERS", [mock_linter]):
            rc = LintTask.execute(validate=True)

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_linter_error_returns_failed(self) -> None:
        mock_linter = _make_mock_linter(set())
        mock_linter.format.side_effect = LinterError
        with patch(
            "dev.tasks.lint.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.lint._INSTALLED_LINTERS", [mock_linter]):
            rc = LintTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_linter_not_installed_returns_failed(self) -> None:
        mock_linter = _make_mock_linter(set())
        mock_linter.format.side_effect = LinterNotInstalledError
        with patch(
            "dev.tasks.lint.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.lint._INSTALLED_LINTERS", [mock_linter]):
            rc = LintTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)


if __name__ == "__main__":
    main()
