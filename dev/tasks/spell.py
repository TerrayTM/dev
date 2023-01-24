from argparse import ArgumentParser, _SubParsersAction
from typing import List, Optional

from dev.constants import ReturnCode
from dev.files import build_file_extensions_filter, select_get_files_function
from dev.output import output
from dev.subprocess import subprocess_run
from dev.tasks.task import Task

CODE_EXTENSIONS = [".py", ".js", ".css", ".html", ".php"]


class SpellTask(Task):
    def _perform(
        self, files: Optional[List[str]] = None, all_files: bool = False,
    ) -> int:
        target_files = None
        try:
            target_files = list(
                select_get_files_function(files, all_files)(
                    [build_file_extensions_filter(CODE_EXTENSIONS)]
                )
            )
        except Exception as error:
            output(str(error))
            return ReturnCode.FAILED

        if not subprocess_run(
            ["cspell", "--no-summary", "--no-progress", "--no-color"] + target_files,
            shell=True,
        ).returncode:
            return ReturnCode.FAILED

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("files", nargs="*")
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")

        return parser
