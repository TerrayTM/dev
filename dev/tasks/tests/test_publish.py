from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.publish import PublishTask


class TestPublish(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_no_dist_dir_returns_ok_without_uploading(self) -> None:
        with (
            patch("dev.tasks.publish.os.path.isdir", return_value=False),
            patch("dev.tasks.publish.run_process") as mock_run,
        ):
            rc = PublishTask.execute()

        mock_run.assert_not_called()
        self.assertEqual(rc, ReturnCode.OK)

    def test_dist_dir_runs_twine_upload(self) -> None:
        with (
            patch("dev.tasks.publish.os.path.isdir", return_value=True),
            patch("dev.tasks.publish.run_process") as mock_run,
        ):
            rc = PublishTask.execute()

        mock_run.assert_called_once()
        self.assertEqual(rc, ReturnCode.OK)


if __name__ == "__main__":
    main()
