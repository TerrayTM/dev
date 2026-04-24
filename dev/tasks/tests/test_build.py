from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.build import BuildTask


class TestBuild(TestCase):
    def setUp(self) -> None:
        OutputConfig.stream = StringIO()

    def test_builds_without_dist_dir(self) -> None:
        with (
            patch("dev.tasks.build.os.path.isdir", return_value=False),
            patch("dev.tasks.build.run_process") as mock_run,
        ):
            rc = BuildTask.execute()

        self.assertEqual(mock_run.call_count, 2)
        self.assertEqual(rc, ReturnCode.OK)

    def test_removes_dist_dir_before_building(self) -> None:
        with (
            patch("dev.tasks.build.os.path.isdir", return_value=True),
            patch("dev.tasks.build.shutil.rmtree") as mock_rmtree,
            patch("dev.tasks.build.run_process"),
        ):
            rc = BuildTask.execute()

        mock_rmtree.assert_called_once_with("dist")
        self.assertEqual(rc, ReturnCode.OK)

    def test_skips_rmtree_when_no_dist_dir(self) -> None:
        with (
            patch("dev.tasks.build.os.path.isdir", return_value=False),
            patch("dev.tasks.build.shutil.rmtree") as mock_rmtree,
            patch("dev.tasks.build.run_process"),
        ):
            BuildTask.execute()

        mock_rmtree.assert_not_called()


if __name__ == "__main__":
    main()
