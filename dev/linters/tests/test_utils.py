import sys
from io import StringIO
from typing import Union
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.exceptions import LinterError, LinterNotInstalledError
from dev.linters.utils import (
    get_linter_program,
    two_phase_lint,
    validate_character_limit,
)
from dev.output import OutputConfig


class TestValidateCharacterLimit(TestCase):
    def setUp(self) -> None:
        self.stream = StringIO()
        OutputConfig.stream = self.stream
        OutputConfig.disable_colors = True

    def tearDown(self) -> None:
        OutputConfig.stream = sys.stdout
        OutputConfig.disable_colors = False

    def test_within_limit_returns_true(self) -> None:
        result = validate_character_limit("file.py", "short line", 1, 88)
        self.assertTrue(result)
        self.assertEqual(self.stream.getvalue(), "")

    def test_exactly_at_limit_returns_true(self) -> None:
        line = "x" * 88
        result = validate_character_limit("file.py", line, 1, 88)
        self.assertTrue(result)
        self.assertEqual(self.stream.getvalue(), "")

    def test_exceeds_limit_returns_false_and_outputs_message(self) -> None:
        line = "x" * 89
        result = validate_character_limit("file.py", line, 5, 88)
        self.assertFalse(result)
        output = self.stream.getvalue()
        self.assertIn("file.py", output)
        self.assertIn("5", output)
        self.assertIn("88", output)


class TestGetLinterProgram(TestCase):
    def test_returns_path_when_found(self) -> None:
        with patch("dev.linters.utils.shutil.which", return_value="/usr/bin/black"):
            result = get_linter_program("black")
        self.assertEqual(result, "/usr/bin/black")

    def test_raises_when_not_found(self) -> None:
        with patch("dev.linters.utils.shutil.which", return_value=None):
            with self.assertRaises(LinterNotInstalledError):
                get_linter_program("black")


class TestTwoPhaseLint(TestCase):
    def _make_result(
        self, stdout: str = "", stderr: str = "", returncode: int = 0
    ) -> MagicMock:
        result = MagicMock()
        result.stdout = stdout
        result.stderr = stderr
        result.returncode = returncode
        return result

    def _no_error(self, line: str) -> None:
        return None

    def _no_formatted(self, line: str) -> None:
        return None

    def test_empty_files_returns_empty_set_without_subprocess_call(self) -> None:
        with patch("subprocess.run") as mock_run:
            result = two_phase_lint(
                [], False, lambda v, f: ["cmd"], self._no_error, self._no_formatted
            )
        self.assertEqual(result, set())
        mock_run.assert_not_called()

    def test_no_errors_no_formatted_returns_empty_set(self) -> None:
        mock_result = self._make_result()
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = two_phase_lint(
                ["a.py"],
                False,
                lambda v, f: ["cmd"],
                self._no_error,
                self._no_formatted,
            )
        self.assertEqual(result, set())
        mock_run.assert_called_once()

    def test_parse_error_returns_str_raises_linter_error(self) -> None:
        mock_result = self._make_result(stderr="error: bad_file.py")

        def parse_error(line: str) -> Union[str, None]:
            return "bad_file.py" if "bad_file" in line else None

        with patch("subprocess.run", return_value=mock_result):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["bad_file.py"],
                    False,
                    lambda v, f: ["cmd"],
                    parse_error,
                    self._no_formatted,
                )

        self.assertIn("bad_file.py", str(ctx.exception))

    def test_parse_error_returns_int_offset_raises_linter_error(self) -> None:
        mock_result = self._make_result(stderr="\npath/to/file.py\nerror here\n")

        def parse_error(line: str) -> Union[int, None]:
            return -1 if "error here" in line else None

        with patch("subprocess.run", return_value=mock_result):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["path/to/file.py"],
                    False,
                    lambda v, f: ["cmd"],
                    parse_error,
                    self._no_formatted,
                )

        self.assertIn("path/to/file.py", str(ctx.exception))

    def test_validate_true_skips_format_run(self) -> None:
        mock_result = self._make_result(stdout="formatted.py\n")

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result = two_phase_lint(
                ["formatted.py"],
                True,
                lambda v, f: ["cmd"],
                self._no_error,
                parse_formatted,
            )

        self.assertIn("formatted.py", result)
        mock_run.assert_called_once()

    def test_validate_false_runs_formatter_on_formatted_files(self) -> None:
        verify_result = self._make_result(stdout="formatted.py\n")
        format_result = self._make_result(returncode=0)

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch(
            "subprocess.run", side_effect=[verify_result, format_result]
        ) as mock_run:
            result = two_phase_lint(
                ["formatted.py"],
                False,
                lambda v, f: ["cmd"],
                self._no_error,
                parse_formatted,
            )

        self.assertIn("formatted.py", result)
        self.assertEqual(mock_run.call_count, 2)

    def test_formatter_failure_raises_linter_error_with_output(self) -> None:
        verify_result = self._make_result(stdout="f.py\n")
        format_result = self._make_result(
            returncode=1, stdout="stdout msg", stderr="stderr msg"
        )

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", side_effect=[verify_result, format_result]):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["f.py"],
                    False,
                    lambda v, f: ["cmd"],
                    self._no_error,
                    parse_formatted,
                )

        error_msg = str(ctx.exception)
        self.assertIn("stdout msg", error_msg)
        self.assertIn("stderr msg", error_msg)
        self.assertIn("problem has occurred", error_msg)

    def test_formatter_failure_with_no_output_raises_generic_error(self) -> None:
        verify_result = self._make_result(stdout="f.py\n")
        format_result = self._make_result(returncode=1, stdout="", stderr="")

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", side_effect=[verify_result, format_result]):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["f.py"],
                    False,
                    lambda v, f: ["cmd"],
                    self._no_error,
                    parse_formatted,
                )

        self.assertIn("problem has occurred", str(ctx.exception))

    def test_ignores_error_suppresses_formatter_failure(self) -> None:
        verify_result = self._make_result(stdout="f.py\n")
        format_result = self._make_result(returncode=1, stdout="out", stderr="err")

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", side_effect=[verify_result, format_result]):
            result = two_phase_lint(
                ["f.py"],
                False,
                lambda v, f: ["cmd"],
                self._no_error,
                parse_formatted,
                ignores_error=True,
            )

        self.assertIn("f.py", result)

    def test_expects_error_produces_empty_base_message(self) -> None:
        verify_result = self._make_result(stdout="f.py\n")
        format_result = self._make_result(returncode=1, stdout="", stderr="")

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", side_effect=[verify_result, format_result]):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["f.py"],
                    False,
                    lambda v, f: ["cmd"],
                    self._no_error,
                    parse_formatted,
                    expects_error=True,
                )

        self.assertNotIn("problem has occurred", str(ctx.exception))

    def test_custom_error_output_stream(self) -> None:
        mock_result = self._make_result(stdout="error: file.py")

        def parse_error(line: str) -> Union[str, None]:
            return "file.py" if "error:" in line else None

        with patch("subprocess.run", return_value=mock_result):
            with self.assertRaises(LinterError) as ctx:
                two_phase_lint(
                    ["file.py"],
                    False,
                    lambda v, f: ["cmd"],
                    parse_error,
                    self._no_formatted,
                    error_output="stdout",
                )

        self.assertIn("file.py", str(ctx.exception))

    def test_custom_formatted_output_stream(self) -> None:
        mock_result = self._make_result(stderr="reformatted.py\n")

        def parse_formatted(line: str) -> Union[str, None]:
            return line if line.endswith(".py") else None

        with patch("subprocess.run", return_value=mock_result):
            result = two_phase_lint(
                ["reformatted.py"],
                True,
                lambda v, f: ["cmd"],
                self._no_error,
                parse_formatted,
                formatted_output="stderr",
            )

        self.assertIn("reformatted.py", result)

    def test_parse_formatted_returns_int_offset(self) -> None:
        mock_result = self._make_result(stdout="\npath/to/formatted.py\nreformatted\n")

        def parse_formatted(line: str) -> Union[int, None]:
            return -1 if line == "reformatted" else None

        with patch("subprocess.run", return_value=mock_result):
            result = two_phase_lint(
                ["path/to/formatted.py"],
                True,
                lambda v, f: ["cmd"],
                self._no_error,
                parse_formatted,
            )

        self.assertIn("path/to/formatted.py", result)


if __name__ == "__main__":
    main()
