from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.spell import SpellTask


class TestSpell(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_fails_when_cspell_not_installed(self) -> None:
        with patch(
            "dev.tasks.spell.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.spell.shutil.which", return_value=None):
            rc = SpellTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)
        self.assertIn("cspell", self._stream.getvalue())

    def test_ok_with_no_files(self) -> None:
        with patch(
            "dev.tasks.spell.select_get_files_function", return_value=lambda _: set()
        ):
            rc = SpellTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_ok_when_cspell_passes(self) -> None:
        with patch(
            "dev.tasks.spell.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.spell.shutil.which", return_value="/usr/bin/cspell"), patch(
            "dev.tasks.spell.run_process"
        ) as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            rc = SpellTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_fails_when_cspell_reports_errors(self) -> None:
        with patch(
            "dev.tasks.spell.select_get_files_function",
            return_value=lambda _: {"file.py"},
        ), patch("dev.tasks.spell.shutil.which", return_value="/usr/bin/cspell"), patch(
            "dev.tasks.spell.run_process"
        ) as mock_run:
            mock_run.return_value = MagicMock(returncode=1)
            rc = SpellTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)


if __name__ == "__main__":
    main()
