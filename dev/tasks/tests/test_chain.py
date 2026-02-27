from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.chain import ChainTask
from dev.tasks.doc import DocTask
from dev.tasks.lint import LintTask
from dev.tasks.spell import SpellTask
from dev.tasks.unused import UnusedTask


class TestChain(TestCase):
    def setUp(self) -> None:
        OutputConfig.stream = StringIO()

    def test_returns_ok_when_all_subtasks_pass(self) -> None:
        with patch.object(
            LintTask, "execute", return_value=ReturnCode.OK
        ), patch.object(
            UnusedTask, "execute", return_value=ReturnCode.OK
        ), patch.object(
            DocTask, "execute", return_value=ReturnCode.OK
        ), patch.object(
            SpellTask, "execute", return_value=ReturnCode.OK
        ):
            rc = ChainTask.execute()

        self.assertEqual(rc, ReturnCode.OK)

    def test_returns_highest_return_code(self) -> None:
        with patch.object(
            LintTask, "execute", return_value=ReturnCode.OK
        ), patch.object(
            UnusedTask, "execute", return_value=ReturnCode.FAILED
        ), patch.object(
            DocTask, "execute", return_value=ReturnCode.OK
        ), patch.object(
            SpellTask, "execute", return_value=ReturnCode.OK
        ):
            rc = ChainTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_runs_all_subtasks(self) -> None:
        with patch.object(
            LintTask, "execute", return_value=ReturnCode.OK
        ) as mock_lint, patch.object(
            UnusedTask, "execute", return_value=ReturnCode.OK
        ) as mock_unused, patch.object(
            DocTask, "execute", return_value=ReturnCode.OK
        ) as mock_doc, patch.object(
            SpellTask, "execute", return_value=ReturnCode.OK
        ) as mock_spell:
            ChainTask.execute()

        mock_lint.assert_called_once()
        mock_unused.assert_called_once()
        mock_doc.assert_called_once()
        mock_spell.assert_called_once()


if __name__ == "__main__":
    main()
