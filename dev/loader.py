import os
from contextlib import contextmanager
from functools import cache
from typing import Any, Dict, Generator, List, Optional, Union
from warnings import warn

import yaml

from dev.constants import CONFIG_FILE, SECRET_CONFIG_FILE
from dev.exceptions import ConfigParseError
from dev.tasks.custom import CustomTask

_TASKS_KEY = "tasks"
_VARIABLES_KEY = "variables"


@contextmanager
def _check_variable_substitution() -> Generator[None, None, None]:
    try:
        yield
    except IndexError:
        raise ConfigParseError("Unable to parse integer variable.")
    except KeyError as error:
        raise ConfigParseError(f"Could not find a definition for variable {error}.")


def _assert_string_or_int(target: Any) -> None:
    if not isinstance(target, int) and not isinstance(target, str):
        raise ConfigParseError(
            f"Target '{target}' is expected to be a string or int type."
        )


def _assert_bool_or_none(target: Any) -> None:
    if target is not None and not isinstance(target, bool):
        raise ConfigParseError(
            f"Target '{target}' is expected to be a bool or null type."
        )


def _assert_string_list_or_none(target: Any) -> None:
    if target is None or isinstance(target, str):
        return

    if isinstance(target, list) and all(isinstance(entry, str) for entry in target):
        return

    raise ConfigParseError(
        f"Target '{target}' is expected to be a string, list of strings, or null type."
    )


def _assert_dictionary(target: Any) -> None:
    if not isinstance(target, dict):
        raise ConfigParseError(
            f"Target '{target}' is expected to be a dictionary type."
        )


def _combine_properties(
    config: Dict[str, Any], secret_config: Dict[str, Any], property_name: str
) -> None:
    if property_name not in secret_config:
        return

    _assert_dictionary(secret_config[property_name])

    if property_name in config:
        _assert_dictionary(config[property_name])

        if (
            len(
                set(config[property_name].keys())
                & set(secret_config[property_name].keys())
            )
            > 0
        ):
            warn(
                "There are conflicting declarations for "
                f"'{property_name}' in the config files."
            )

    config.setdefault(property_name, {}).update(secret_config[property_name])


def _format_script(
    script: Optional[Union[str, List[str]]], variables: Dict[str, Any]
) -> Optional[List[str]]:
    if script is None:
        return None

    target = [script] if isinstance(script, str) else script

    with _check_variable_substitution():
        return [entry.replace("{}", "{{}}").format(**variables) for entry in target]


def read_config(config_path: str) -> Dict[str, Any]:
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


@cache
def load_combined_config() -> Dict[str, Any]:
    config = read_config(CONFIG_FILE)
    secret_config = read_config(SECRET_CONFIG_FILE)

    _combine_properties(config, secret_config, _TASKS_KEY)
    _combine_properties(config, secret_config, _VARIABLES_KEY)

    return config


@cache
def load_variables() -> Dict[str, Union[str, int]]:
    variables = {}
    config = load_combined_config()

    if _VARIABLES_KEY in config:
        _assert_dictionary(config[_VARIABLES_KEY])

        for variable, value in config[_VARIABLES_KEY].items():
            _assert_string_or_int(value)
            variables[variable] = value

    return variables


def load_tasks_from_config(dynamic_task_map: Dict[str, Any]) -> List[CustomTask]:
    tasks = []
    config = load_combined_config()
    variables = load_variables()

    if _TASKS_KEY in config:
        _assert_dictionary(config[_TASKS_KEY])

        for name, definition in config[_TASKS_KEY].items():
            _assert_dictionary(definition)

            run_script = definition.get("run")
            pre_script = definition.get("pre")
            post_script = definition.get("post")
            run_parallel = definition.get("parallel")
            env = definition.get("env")

            _assert_string_list_or_none(run_script)
            _assert_string_list_or_none(pre_script)
            _assert_string_list_or_none(post_script)
            _assert_bool_or_none(run_parallel)
            _assert_string_list_or_none(env)

            with _check_variable_substitution():
                env_vars = (
                    None if env is None else {key: str(variables[key]) for key in env}
                )

            tasks.append(
                CustomTask(
                    name,
                    _format_script(run_script, variables),
                    _format_script(pre_script, variables),
                    _format_script(post_script, variables),
                    run_parallel or False,
                    dynamic_task_map,
                    env_vars,
                )
            )

    return tasks
