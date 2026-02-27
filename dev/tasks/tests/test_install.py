from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.install import InstallTask


class TestInstall(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_default_install_uses_no_deps(self) -> None:
        with patch("dev.tasks.install.run_process") as mock_run:
            rc = InstallTask.execute()

        self.assertIn("--no-deps", mock_run.call_args[0][0])
        self.assertEqual(rc, ReturnCode.OK)

    def test_include_dependencies_omits_no_deps(self) -> None:
        with patch("dev.tasks.install.run_process") as mock_run:
            rc = InstallTask.execute(include_dependencies=True)

        self.assertNotIn("--no-deps", mock_run.call_args[0][0])
        self.assertEqual(rc, ReturnCode.OK)

    def test_dependencies_only_fails_without_setup_file(self) -> None:
        with patch("dev.tasks.install.os.path.isfile", return_value=False):
            rc = InstallTask.execute(dependencies_only=True)

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_dependencies_only_fails_with_parse_failure(self) -> None:
        with patch("dev.tasks.install.os.path.isfile", return_value=True), patch(
            "dev.tasks.install.parse_setup_file", return_value=None
        ):
            rc = InstallTask.execute(dependencies_only=True)

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_dependencies_only_ok_with_no_dependencies(self) -> None:
        mock_setup = MagicMock()
        mock_setup.install_requires = []
        with patch("dev.tasks.install.os.path.isfile", return_value=True), patch(
            "dev.tasks.install.parse_setup_file", return_value=mock_setup
        ), patch("dev.tasks.install.run_process") as mock_run:
            rc = InstallTask.execute(dependencies_only=True)

        mock_run.assert_not_called()
        self.assertEqual(rc, ReturnCode.OK)

    def test_dependencies_only_installs_dependencies(self) -> None:
        mock_setup = MagicMock()
        mock_setup.install_requires = ["requests", "pyyaml"]
        with patch("dev.tasks.install.os.path.isfile", return_value=True), patch(
            "dev.tasks.install.parse_setup_file", return_value=mock_setup
        ), patch("dev.tasks.install.run_process") as mock_run:
            rc = InstallTask.execute(dependencies_only=True)

        args = mock_run.call_args[0][0]
        self.assertIn("requests", args)
        self.assertIn("pyyaml", args)
        self.assertEqual(rc, ReturnCode.OK)


if __name__ == "__main__":
    main()
