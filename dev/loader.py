import os
from typing import List

import yaml

from dev.constants import CONFIG_FILE
from dev.exceptions import ConfigParseError
from dev.tasks.custom import CustomTask


def load_tasks_from_config() -> List[CustomTask]:
    tasks = []

    if os.path.isfile(CONFIG_FILE):
        config = None

        with open(CONFIG_FILE) as file:
            try:
                config = yaml.safe_load(file.read())
            except yaml.scanner.ScannerError:
                raise ConfigParseError()

        if config is None:
            return []

        try:
            for name, definition in config["tasks"].items():
                tasks.append(
                    (
                        name,
                        CustomTask(
                            definition.get("run"),
                            definition.get("pre"),
                            definition.get("post"),
                        ),
                    )
                )
        except KeyError:
            raise ConfigParseError()

    return tasks
