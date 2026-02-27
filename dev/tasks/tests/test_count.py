import os
import tempfile
from io import StringIO
from unittest import TestCase, main
from unittest.mock import patch

from dev.constants import ReturnCode
from dev.output import OutputConfig
from dev.tasks.count import CountTask


class TestCount(TestCase):
    def setUp(self) -> None:
        self._stream = StringIO()
        OutputConfig.stream = self._stream

    def test_counts_lines(self) -> None:
        fd, path = tempfile.mkstemp(suffix=".py")
        with os.fdopen(fd, "w") as f:
            f.write("line1\nline2\nline3\n")

        try:
            with patch("dev.tasks.count.get_repo_files", return_value={path}):
                rc = CountTask.execute()
        finally:
            os.unlink(path)

        self.assertEqual(rc, ReturnCode.OK)
        self.assertIn("3", self._stream.getvalue())

    def test_no_files_outputs_zero(self) -> None:
        with patch("dev.tasks.count.get_repo_files", return_value=set()):
            rc = CountTask.execute()

        self.assertEqual(rc, ReturnCode.OK)
        self.assertIn("0", self._stream.getvalue())

    def test_by_author_fails_when_git_not_found(self) -> None:
        with patch("dev.tasks.count.subprocess.run", side_effect=FileNotFoundError):
            rc = CountTask.execute(by_author=True)

        self.assertEqual(rc, ReturnCode.FAILED)


if __name__ == "__main__":
    main()
