import os
import tempfile
from pathlib import Path
from unittest import TestCase, main

from dev.constants import ReturnCode
from dev.tasks.clean import CleanTask


class TestClean(TestCase):
    def setUp(self) -> None:
        self._original_dir = os.getcwd()
        self._temp_dir = tempfile.mkdtemp()
        os.chdir(self._temp_dir)

    def tearDown(self) -> None:
        os.chdir(self._original_dir)

    def test_removes_pyc_files(self) -> None:
        pyc_file = Path(self._temp_dir) / "module.pyc"
        pyc_file.touch()

        rc = CleanTask.execute()

        self.assertFalse(pyc_file.exists())
        self.assertEqual(rc, ReturnCode.OK)

    def test_removes_pycache_dirs(self) -> None:
        cache_dir = Path(self._temp_dir) / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.pyc").touch()

        rc = CleanTask.execute()

        self.assertFalse(cache_dir.exists())
        self.assertEqual(rc, ReturnCode.OK)

    def test_returns_ok_with_nothing_to_clean(self) -> None:
        rc = CleanTask.execute()
        self.assertEqual(rc, ReturnCode.OK)


if __name__ == "__main__":
    main()
