from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.loader import _DevConfig
from dev.output import OutputConfig
from dev.tasks.env import EnvTask


class TestEnv(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_runs_command_with_env_vars(self) -> None:
        with (
            patch(
                "dev.tasks.env.load_combined_config",
                return_value=_DevConfig(variables={"FOO": "bar"}),
            ),
            patch("dev.tasks.env.run_process") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0)
            rc = EnvTask.execute(command=["echo"])

        env = mock_run.call_args[1]["env"]
        self.assertEqual(env.get("FOO"), "bar")
        self.assertEqual(rc, ReturnCode.OK)

    def test_failed_command_returns_failed(self) -> None:
        with (
            patch(
                "dev.tasks.env.load_combined_config",
                return_value=_DevConfig(variables={}),
            ),
            patch("dev.tasks.env.run_process") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=1)
            rc = EnvTask.execute(command=["false"])

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_verbose_outputs_variable_table(self) -> None:
        with (
            patch(
                "dev.tasks.env.load_combined_config",
                return_value=_DevConfig(variables={"KEY": "val"}),
            ),
            patch("dev.tasks.env.run_process") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0)
            EnvTask.execute(command=["echo"], verbose=True)

        self.assertIn("KEY", self._stream.getvalue())


if __name__ == "__main__":
    main()
