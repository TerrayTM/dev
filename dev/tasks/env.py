import os
from argparse import ArgumentParser, _SubParsersAction
from typing import List

import tabulate

from dev.constants import ReturnCode
from dev.loader import load_variables
from dev.output import output
from dev.process import run_process
from dev.tasks.task import Task


class EnvTask(Task):
    def _perform(self, command: List[str], verbose: bool = False) -> int:
        env_vars = {key: str(value) for key, value in load_variables().items()}

        if verbose and env_vars:
            output(
                tabulate.tabulate(
                    list(env_vars.items()), ["key", "value"], tablefmt="outline"
                )
            )

        return (
            ReturnCode.OK
            if not run_process(
                command, shell=True, env={**os.environ, **env_vars}
            ).returncode
            else ReturnCode.FAILED
        )

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("command", nargs="+")
        parser.add_argument("-v", "--verbose", action="store_true", dest="verbose")

        return parser
