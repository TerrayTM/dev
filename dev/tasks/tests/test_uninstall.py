from io import StringIO
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.uninstall import UninstallTask


class TestUninstall(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_fails_without_setup_file(self) -> None:
        with patch("dev.tasks.uninstall.os.path.isfile", return_value=False):
            rc = UninstallTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_fails_with_invalid_setup_file(self) -> None:
        with patch("dev.tasks.uninstall.os.path.isfile", return_value=True), patch(
            "dev.tasks.uninstall.parse_setup_file", return_value=None
        ):
            rc = UninstallTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_fails_with_no_package_name(self) -> None:
        mock_setup = MagicMock()
        mock_setup.name = None
        with patch("dev.tasks.uninstall.os.path.isfile", return_value=True), patch(
            "dev.tasks.uninstall.parse_setup_file", return_value=mock_setup
        ):
            rc = UninstallTask.execute()

        self.assertEqual(rc, ReturnCode.FAILED)

    def test_uninstalls_package(self) -> None:
        mock_setup = MagicMock()
        mock_setup.name = "my-pkg"
        with (
            patch("dev.tasks.uninstall.os.path.isfile", return_value=True),
            patch("dev.tasks.uninstall.parse_setup_file", return_value=mock_setup),
            patch("dev.tasks.uninstall.os.path.isdir", return_value=False),
            patch("dev.tasks.uninstall.run_process") as mock_run,
        ):
            rc = UninstallTask.execute()

        self.assertIn("my-pkg", mock_run.call_args[0][0])
        self.assertEqual(rc, ReturnCode.OK)

    def test_removes_egg_info_folder(self) -> None:
        mock_setup = MagicMock()
        mock_setup.name = "my-pkg"
        with (
            patch("dev.tasks.uninstall.os.path.isfile", return_value=True),
            patch("dev.tasks.uninstall.parse_setup_file", return_value=mock_setup),
            patch("dev.tasks.uninstall.run_process"),
            patch("dev.tasks.uninstall.os.path.isdir", return_value=True),
            patch("dev.tasks.uninstall.shutil.rmtree") as mock_rmtree,
        ):
            rc = UninstallTask.execute()

        mock_rmtree.assert_called_once_with("my_pkg.egg-info")
        self.assertEqual(rc, ReturnCode.OK)


if __name__ == "__main__":
    main()
