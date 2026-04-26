import os
from contextlib import contextmanager
from typing import Dict, Generator, List, Optional, Union
from warnings import warn

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

from dev.constants import CONFIG_FILE, SECRET_CONFIG_FILE
from dev.exceptions import ConfigParseError
from dev.tasks.custom import CustomTask
from dev.tasks.task import DynamicTaskMap

_ScriptValue = Optional[Union[str, List[str]]]


class _TaskDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run: _ScriptValue = None
    pre: _ScriptValue = None
    post: _ScriptValue = None
    parallel: Optional[bool] = None
    env: _ScriptValue = None


class _DevConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tasks: Optional[Dict[str, _TaskDefinition]] = None
    variables: Optional[Dict[str, Union[str, int]]] = None


@contextmanager
def _check_variable_substitution() -> Generator[None, None, None]:
    try:
        yield
    except IndexError:
        raise ConfigParseError("Unable to parse integer variable.")
    except KeyError as error:
        raise ConfigParseError(f"Could not find a definition for variable {error}.")


def _format_script(
    script: _ScriptValue, variables: Dict[str, Union[str, int]]
) -> Optional[List[str]]:
    if script is None:
        return None

    target = [script] if isinstance(script, str) else script

    with _check_variable_substitution():
        return [entry.replace("{}", "{{}}").format(**variables) for entry in target]


def read_config(config_path: str) -> _DevConfig:
    if not os.path.isfile(config_path):
        return _DevConfig()

    with open(config_path) as file:
        try:
            config = yaml.safe_load(file.read())
        except yaml.scanner.ScannerError:
            raise ConfigParseError(f"Failed to parse YAML file '{config_path}'.")

    if config is None:
        return _DevConfig()

    try:
        parsed = _DevConfig.model_validate(config)
    except ValidationError as error:
        raise ConfigParseError(str(error)) from error

    return parsed


def load_combined_config() -> _DevConfig:
    main = read_config(CONFIG_FILE)
    secret = read_config(SECRET_CONFIG_FILE)

    combined_tasks = {**(main.tasks or {}), **(secret.tasks or {})}
    combined_variables = {**(main.variables or {}), **(secret.variables or {})}

    if len(combined_tasks) != len(main.tasks or {}) + len(secret.tasks or {}):
        warn("There are conflicting declarations for 'tasks' in the config files.")

    if len(combined_variables) != len(main.variables or {}) + len(
        secret.variables or {}
    ):
        warn("There are conflicting declarations for 'variables' in the config files.")

    # Cast it back to None if needed
    return _DevConfig(
        tasks=combined_tasks or None, variables=combined_variables or None
    )


def load_tasks_from_config(dynamic_task_map: DynamicTaskMap) -> List[CustomTask]:
    config = load_combined_config()

    if not config.tasks:
        return []

    variables = config.variables or {}
    tasks: List[CustomTask] = []
    for name, definition in config.tasks.items():
        env_list = (
            None
            if definition.env is None
            else (
                [definition.env] if isinstance(definition.env, str) else definition.env
            )
        )

        with _check_variable_substitution():
            env_vars = (
                None
                if env_list is None
                else {key: str(variables[key]) for key in env_list}
            )

        tasks.append(
            CustomTask(
                name,
                _format_script(definition.run, variables),
                _format_script(definition.pre, variables),
                _format_script(definition.post, variables),
                definition.parallel or False,
                dynamic_task_map,
                env_vars,
            )
        )

    return tasks
