from unittest import TestCase, main

from dev.files import (
    build_file_extensions_filter,
    filter_not_cache_files,
    filter_not_python_underscore_files,
    filter_not_unit_test_files,
    filter_python_files,
    filter_unit_test_files,
)


class TestOutput(TestCase):
    def test_build_file_extensions_filter(self) -> None:
        filter_ = build_file_extensions_filter({".abc", ".def"})

        self.assertTrue(filter_("x.abc"))
        self.assertTrue(filter_("x.def"))
        self.assertFalse(filter_("x.xyz"))

    def test_filter_python_files(self) -> None:
        self.assertTrue(filter_python_files("main.py"))

        self.assertFalse(filter_python_files("main.pyc"))
        self.assertFalse(filter_python_files("main.txt"))

    def test_filter_unit_test_files(self) -> None:
        self.assertTrue(filter_unit_test_files("test_abc.py"))

        self.assertFalse(filter_unit_test_files("abc_test.py"))
        self.assertFalse(filter_unit_test_files("a.py"))

    def test_filter_not_unit_test_files(self) -> None:
        self.assertTrue(filter_not_unit_test_files("a.py"))
        self.assertTrue(filter_not_unit_test_files("abc_test.py"))

        self.assertFalse(filter_not_unit_test_files("test_abc.py"))

    def test_filter_not_cache_files(self) -> None:
        self.assertTrue(filter_not_cache_files("a.py"))

        self.assertFalse(filter_not_cache_files("__pycache__/module.cpython-311.pyc"))
        self.assertFalse(filter_not_cache_files("/path/__pycache__/module.pyc"))

    def test_filter_not_python_underscore_files(self) -> None:
        self.assertTrue(filter_not_python_underscore_files("a.py"))
        self.assertTrue(filter_not_python_underscore_files("test_abc.py"))

        self.assertFalse(filter_not_python_underscore_files("__init__.py"))
        self.assertFalse(filter_not_python_underscore_files("__main__.py"))


if __name__ == "__main__":
    main()
