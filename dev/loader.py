import os
from typing import Any, Dict, List
from warnings import warn

import yaml

from dev.constants import CONFIG_FILE, SECRET_CONFIG_FILE
from dev.exceptions import ConfigParseError
from dev.tasks.custom import CustomTask

_TASKS_KEY = "tasks"


def _assert_string_or_none(target: Any) -> None:
    if target is not None and not isinstance(target, str):
        raise ConfigParseError(
            f"Target '{target}' is expected to be a string or null type."
        )


def _assert_dictionary(target: Any) -> None:
    if not isinstance(target, dict):
        raise ConfigParseError(
            f"Target '{target}' is expected to be a dictionary type."
        )


def _read_config(config_path: str) -> Dict[str, Any]:
    config = {}

    if os.path.isfile(config_path):
        with open(config_path) as file:
            try:
                config = yaml.safe_load(file.read())
            except yaml.scanner.ScannerError:
                raise ConfigParseError(f"Failed to parse YAML file '{config_path}'.")

        if config is None:
            return {}

        _assert_dictionary(config)

    return config


def load_tasks_from_config() -> List[CustomTask]:
    tasks = []

    config = _read_config(CONFIG_FILE)
    secret_config = _read_config(SECRET_CONFIG_FILE)

    if _TASKS_KEY in secret_config:
        _assert_dictionary(secret_config[_TASKS_KEY])

        if _TASKS_KEY in config:
            _assert_dictionary(config[_TASKS_KEY])

            if (
                len(
                    set(config[_TASKS_KEY].keys())
                    & set(secret_config[_TASKS_KEY].keys())
                )
                > 0
            ):
                warn("There are conflicting task declarations in the config files.")

        config.setdefault(_TASKS_KEY, {}).update(secret_config[_TASKS_KEY])

    if _TASKS_KEY in config:
        _assert_dictionary(config[_TASKS_KEY])

        for name, definition in config[_TASKS_KEY].items():
            _assert_dictionary(definition)

            run_script = definition.get("run")
            pre_script = definition.get("pre")
            post_script = definition.get("post")

            _assert_string_or_none(run_script)
            _assert_string_or_none(pre_script)
            _assert_string_or_none(post_script)

            tasks.append((name, CustomTask(run_script, pre_script, post_script,),))

    return tasks
