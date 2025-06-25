import subprocess
from argparse import ArgumentParser, _SubParsersAction
from typing import List, Optional

from dev.constants import ReturnCode
from dev.files import filter_python_files, select_get_files_function
from dev.output import output
from dev.tasks.task import Task

_UNUSED_IMPORT_ERROR = "W0611"


class UnusedTask(Task):
    def _perform(
        self, files: Optional[List[str]] = None, all_files: bool = False
    ) -> int:
        target_files = None
        try:
            target_files = list(
                select_get_files_function(files, all_files)([filter_python_files])
            )
        except Exception as error:
            output(str(error))
            return ReturnCode.FAILED

        if len(target_files) > 0:
            rc = ReturnCode.OK
            result = subprocess.run(
                ["pylint"] + target_files,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                encoding="utf8",
            )

            for line in result.stdout.split("\n"):
                if _UNUSED_IMPORT_ERROR in line:
                    rc = ReturnCode.FAILED
                    output(line)

            return rc

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("files", nargs="*")
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")

        return parser
