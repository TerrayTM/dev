import os
import tempfile
from typing import List
from unittest import TestCase, main
from unittest.mock import patch

from dev.exceptions import ConfigParseError
from dev.loader import (
    load_combined_config,
    load_tasks_from_config,
    load_variables,
    read_config,
)


class TestReadConfig(TestCase):
    def setUp(self) -> None:
        self._temp_files: List[str] = []

    def tearDown(self) -> None:
        for path in self._temp_files:
            os.unlink(path)

    def _write(self, content: str) -> str:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        self._temp_files.append(path)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def test_nonexistent_file_returns_empty(self) -> None:
        self.assertEqual(read_config("/nonexistent/path/config.yaml"), {})

    def test_valid_yaml(self) -> None:
        path = self._write("key: value\nnumber: 42")
        self.assertEqual(read_config(path), {"key": "value", "number": 42})

    def test_empty_file_returns_empty(self) -> None:
        path = self._write("")
        self.assertEqual(read_config(path), {})

    def test_invalid_yaml_raises(self) -> None:
        path = self._write("key:\n\tbad_indent")
        with self.assertRaises(ConfigParseError):
            read_config(path)

    def test_non_dict_yaml_raises(self) -> None:
        path = self._write("- item1\n- item2")
        with self.assertRaises(ConfigParseError):
            read_config(path)


class TestLoadCombinedConfig(TestCase):
    def setUp(self) -> None:
        load_combined_config.cache_clear()

    def test_merges_variables_from_both_configs(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[{"variables": {"a": 1}}, {"variables": {"b": 2}}],
        ):
            config = load_combined_config()
        self.assertEqual(config["variables"], {"a": 1, "b": 2})

    def test_no_secret_config(self) -> None:
        with patch("dev.loader.read_config", side_effect=[{"variables": {"a": 1}}, {}]):
            config = load_combined_config()
        self.assertEqual(config["variables"], {"a": 1})

    def test_empty_configs(self) -> None:
        with patch("dev.loader.read_config", side_effect=[{}, {}]):
            config = load_combined_config()
        self.assertEqual(config, {})


class TestLoadVariables(TestCase):
    def setUp(self) -> None:
        load_combined_config.cache_clear()
        load_variables.cache_clear()

    def test_empty_when_no_variables(self) -> None:
        with patch("dev.loader.read_config", side_effect=[{}, {}]):
            variables = load_variables()
        self.assertEqual(variables, {})

    def test_extracts_string_and_int_variables(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[{"variables": {"name": "foo", "count": 5}}, {}],
        ):
            variables = load_variables()
        self.assertEqual(variables, {"name": "foo", "count": 5})

    def test_invalid_variable_type_raises(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[{"variables": {"bad": [1, 2, 3]}}, {}],
        ):
            with self.assertRaises(ConfigParseError):
                load_variables()


class TestLoadTasksFromConfig(TestCase):
    def setUp(self) -> None:
        load_combined_config.cache_clear()
        load_variables.cache_clear()

    def test_no_tasks_returns_empty(self) -> None:
        with patch("dev.loader.read_config", side_effect=[{}, {}]):
            tasks = load_tasks_from_config({})
        self.assertEqual(tasks, [])

    def test_creates_custom_task(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[{"tasks": {"greet": {"run": ["echo hello"]}}}, {}],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_name(), "greet")

    def test_variable_substitution_in_scripts(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                {
                    "variables": {"cmd": "echo"},
                    "tasks": {"greet": {"run": ["{cmd} hello"]}},
                },
                {},
            ],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_name(), "greet")

    def test_multiple_tasks_created(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                {
                    "tasks": {
                        "task_a": {"run": ["echo a"]},
                        "task_b": {"run": ["echo b"]},
                    }
                },
                {},
            ],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 2)
        self.assertEqual({task.task_name() for task in tasks}, {"task_a", "task_b"})


if __name__ == "__main__":
    main()
