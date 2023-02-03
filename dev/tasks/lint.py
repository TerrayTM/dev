from argparse import ArgumentParser, _SubParsersAction
from typing import List, Optional

from dev.constants import ReturnCode
from dev.exceptions import LinterError
from dev.files import build_file_extensions_filter, select_get_files_function
from dev.linters.csharp import CSharpLinter
from dev.linters.javascript import JavaScriptLinter
from dev.linters.python import PythonLinter
from dev.output import output
from dev.tasks.task import Task

_INSTALLED_LINTERS = (PythonLinter, JavaScriptLinter, CSharpLinter)
_SUPPORTED_EXTENSIONS = tuple(linter.get_extension() for linter in _INSTALLED_LINTERS)


class LintTask(Task):
    def _plural(self, count: int) -> str:
        return "" if count == 1 else "s"

    def _perform(
        self,
        files: Optional[List[str]] = None,
        all_files: bool = False,
        validate: bool = False,
        line_length: Optional[int] = None,
    ) -> int:
        target_files = None
        formatted = set()

        try:
            target_files = select_get_files_function(files, all_files)(
                [build_file_extensions_filter(_SUPPORTED_EXTENSIONS)]
            )

            for linter in _INSTALLED_LINTERS:
                width = line_length if line_length is not None else linter.get_width()
                formatted |= linter.format(target_files, width, validate)
        except (LinterError, ValueError) as error:
            output(str(error))
            return ReturnCode.FAILED

        if len(formatted) > 0:
            if validate:
                output("The following files are mis-formatted:")
                for file in formatted:
                    output(f"  - {file}")

                return ReturnCode.FAILED

            output(
                f"Checked {len(target_files)} file{self._plural(len(target_files))} "
                f"formatted {len(formatted)} file{self._plural(len(formatted))}."
            )

        return ReturnCode.OK

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("files", nargs="*")
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")
        parser.add_argument("-v", "--validate", action="store_true", dest="validate")
        parser.add_argument("-l", "--line-length", type=int, dest="line_length")

        return parser
