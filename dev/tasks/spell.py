import shutil
from argparse import ArgumentParser, _SubParsersAction
from typing import List, Optional

from dev.constants import CODE_EXTENSIONS, ReturnCode
from dev.files import build_file_extensions_filter, select_get_files_function
from dev.output import output
from dev.process import run_process
from dev.tasks.task import Task


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

        program = shutil.which("cspell")
        if program is None:
            output("Spell checker 'cspell' is not found.")
            output(
                "Install spell checker using 'npm install -g cspell@latest' "
                "then rerun dev spell."
            )
            return ReturnCode.FAILED

        if (
            len(target_files) > 0
            and run_process(
                [program, "--no-summary", "--no-progress", "--no-color"] + target_files
            ).returncode
        ):
            return ReturnCode.FAILED

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("files", nargs="*")
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")

        return parser
