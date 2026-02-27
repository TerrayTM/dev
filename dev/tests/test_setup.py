import os
import tempfile
from typing import List
from unittest import TestCase, main

from dev.setup import parse_setup_file


class TestParseSetupFile(TestCase):
    def setUp(self) -> None:
        self._temp_files: List[str] = []

    def tearDown(self) -> None:
        for path in self._temp_files:
            os.unlink(path)

    def _write(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".py")
        self._temp_files.append(path)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_parses_name_and_install_requires(self) -> None:
        path = self._write('setup(name="my-pkg", install_requires=["a", "b"])')
        result = parse_setup_file(path)
        assert result is not None
        self.assertEqual(result.name, "my-pkg")
        self.assertEqual(result.install_requires, ["a", "b"])

    def test_install_requires_as_top_level_assignment(self) -> None:
        path = self._write('install_requires = ["dep1", "dep2"]\nsetup(name="pkg")')
        result = parse_setup_file(path)
        assert result is not None
        self.assertEqual(result.install_requires, ["dep1", "dep2"])

    def test_syntax_error_returns_none(self) -> None:
        path = self._write("def")
        result = parse_setup_file(path)
        self.assertIsNone(result)

    def test_no_name_is_none(self) -> None:
        path = self._write('setup(install_requires=["a"])')
        result = parse_setup_file(path)
        assert result is not None
        self.assertIsNone(result.name)

    def test_empty_install_requires(self) -> None:
        path = self._write('setup(name="pkg", install_requires=[])')
        result = parse_setup_file(path)
        assert result is not None
        self.assertEqual(result.install_requires, [])

    def test_no_setup_call(self) -> None:
        path = self._write("x = 1")
        result = parse_setup_file(path)
        assert result is not None
        self.assertIsNone(result.name)
        self.assertEqual(result.install_requires, [])

    def test_duplicate_install_requires_raises(self) -> None:
        path = self._write(
            'install_requires = ["a"]\nsetup(name="pkg", install_requires=["b"])'
        )
        with self.assertRaises(ValueError):
            parse_setup_file(path)

    def test_install_requires_not_list_raises(self) -> None:
        path = self._write('setup(name="pkg", install_requires="dep")')
        with self.assertRaises(ValueError):
            parse_setup_file(path)


if __name__ == "__main__":
    main()
