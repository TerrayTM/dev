import os
import tempfile
from typing import List
from unittest import TestCase, main
from unittest.mock import patch

from dev.exceptions import ConfigParseError
from dev.loader import (
    _DevConfig,
    _TaskDefinition,
    load_combined_config,
    load_tasks_from_config,
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
        config = read_config("/nonexistent/path/config.yaml")
        self.assertIsNone(config.tasks)
        self.assertIsNone(config.variables)

    def test_valid_yaml(self) -> None:
        path = self._write("variables:\n  name: foo\n  count: 5")
        config = read_config(path)
        self.assertEqual(config.variables, {"name": "foo", "count": 5})

    def test_empty_file_returns_empty(self) -> None:
        path = self._write("")
        config = read_config(path)
        self.assertIsNone(config.tasks)
        self.assertIsNone(config.variables)

    def test_invalid_yaml_raises(self) -> None:
        path = self._write("key:\n\tbad_indent")
        with self.assertRaises(ConfigParseError):
            read_config(path)

    def test_non_dict_yaml_raises(self) -> None:
        path = self._write("- item1\n- item2")
        with self.assertRaises(ConfigParseError):
            read_config(path)


class TestLoadCombinedConfig(TestCase):
    def test_merges_variables_from_both_configs(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                _DevConfig(variables={"a": 1}),
                _DevConfig(variables={"b": 2}),
            ],
        ):
            config = load_combined_config()
        self.assertEqual(config.variables, {"a": 1, "b": 2})

    def test_no_secret_config(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[_DevConfig(variables={"a": 1}), _DevConfig()],
        ):
            config = load_combined_config()
        self.assertEqual(config.variables, {"a": 1})

    def test_empty_configs(self) -> None:
        with patch("dev.loader.read_config", side_effect=[_DevConfig(), _DevConfig()]):
            config = load_combined_config()
        self.assertIsNone(config.tasks)
        self.assertIsNone(config.variables)


class TestLoadTasksFromConfig(TestCase):
    def test_creates_custom_task(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                _DevConfig(tasks={"greet": _TaskDefinition(run=["echo hello"])}),
                _DevConfig(),
            ],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_name(), "greet")

    def test_variable_substitution_in_scripts(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                _DevConfig(
                    variables={"cmd": "echo"},
                    tasks={"greet": _TaskDefinition(run=["{cmd} hello"])},
                ),
                _DevConfig(),
            ],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].task_name(), "greet")

    def test_env_undefined_variable_raises(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                _DevConfig(
                    tasks={"serve": _TaskDefinition(run=["server"], env=["port"])}
                ),
                _DevConfig(),
            ],
        ):
            with self.assertRaises(ConfigParseError):
                load_tasks_from_config({})

    def test_multiple_tasks_created(self) -> None:
        with patch(
            "dev.loader.read_config",
            side_effect=[
                _DevConfig(
                    tasks={
                        "task_a": _TaskDefinition(run=["echo a"]),
                        "task_b": _TaskDefinition(run=["echo b"]),
                    }
                ),
                _DevConfig(),
            ],
        ):
            tasks = load_tasks_from_config({})
        self.assertEqual(len(tasks), 2)
        self.assertEqual({task.task_name() for task in tasks}, {"task_a", "task_b"})


if __name__ == "__main__":
    main()
