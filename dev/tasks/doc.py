import ast
import re
from argparse import ArgumentParser, _SubParsersAction
from enum import Enum, auto
from io import TextIOWrapper
from typing import List, NamedTuple, Optional, Tuple

from dev.constants import ReturnCode
from dev.files import (
    filter_not_python_underscore_files,
    filter_not_unit_test_files,
    filter_python_files,
    get_changed_repo_files,
    get_repo_files,
)
from dev.output import output
from dev.tasks.task import Task

SPECIAL_PARAMETER_NAMES = ("self", "cls")


class _ValidationType(Enum):
    PARAMETER = auto()
    RETURN = auto()
    DOCSTRING_FORMAT = auto()
    DOCSTRING_PRESENCE = auto()


class _ValidationResult(NamedTuple):
    validation_type: _ValidationType
    line_number: int
    name: str


class _Parameter(NamedTuple):
    name: str
    annotation: Optional[str]
    default_value: Optional[str]


def _generate_docstring(
    parameters: List[_Parameter],
    return_annotation: Optional[str],
    space_offset: int,
    validation_mode: bool,
) -> str:
    spaces = " " * space_offset * int(not validation_mode)
    function_placeholder = "Placeholder function documentation string."
    argument_placeholder = "Placeholder argument documentation string."
    result_placeholder = "Placeholder result documentation string."
    raw = lambda string: string

    if validation_mode:
        function_placeholder = r"(?:.|\n)*?"
        argument_placeholder = r"(?:.|\n)*?"
        result_placeholder = r"(?:.|\n)*?"
        raw = lambda string: re.escape(string)

    comment = f"{spaces}{function_placeholder}"

    if len(parameters) > 0:
        comment += f"\n\n{spaces}Parameters\n{spaces}----------\n"

        for index, parameter in enumerate(parameters):
            annotation_string = raw(
                parameter.annotation if parameter.annotation is not None else "???"
            )
            default_string = (
                raw(f" (default={parameter.default_value})")
                if parameter.default_value is not None
                else ""
            )

            comment += (
                f"{spaces}{parameter.name} : {annotation_string}{default_string}"
                f"\n{spaces}    {argument_placeholder}"
            )

            if index + 1 != len(parameters):
                comment += "\n\n"

    if return_annotation != "None":
        return_string = raw(
            return_annotation if return_annotation is not None else "???"
        )

        if len(parameters) > 0:
            comment += "\n"

        comment += (
            f"\n{spaces}Returns\n{spaces}-------"
            f"\n{spaces}result : {return_string}\n{spaces}    {result_placeholder}"
        )

    return comment if validation_mode else f'{spaces}"""\n{comment}\n{spaces}"""\n'


class _Visitor(ast.NodeVisitor):
    def __init__(
        self,
        source: str,
        function_docs: List[Tuple[int, str]],
        validation_results: List[_ValidationResult],
        validation_mode: bool,
    ) -> None:
        self._source = source
        self._function_docs = function_docs
        self._validation_results = validation_results
        self._validation_mode = validation_mode

    def _node_to_string(
        self, node: Optional[ast.AST], strip_quotes: bool = True
    ) -> Optional[str]:
        if node is None:
            return None

        string = ast.get_source_segment(self._source, node)

        if strip_quotes:
            return string.strip('"')

        return string

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        padding = [None] * (len(node.args.args) - len(node.args.defaults))
        default_values = [
            self._node_to_string(default_node, False)
            for default_node in node.args.defaults
        ]
        parameters = [
            _Parameter(arg.arg, self._node_to_string(arg.annotation), default_value)
            for arg, default_value in zip(node.args.args, padding + default_values)
            if arg.arg not in SPECIAL_PARAMETER_NAMES
        ]
        return_annotation = self._node_to_string(node.returns)

        for parameter in parameters:
            if parameter.annotation is None:
                self._validation_results.append(
                    _ValidationResult(
                        _ValidationType.PARAMETER, node.lineno, parameter.name
                    )
                )

        if return_annotation is None:
            self._validation_results.append(
                _ValidationResult(_ValidationType.RETURN, node.lineno, node.name)
            )

        node_docstring = ast.get_docstring(node)

        if self._validation_mode or node_docstring is None:
            docstring = _generate_docstring(
                parameters,
                return_annotation,
                node.col_offset + 4,
                self._validation_mode,
            )

            if self._validation_mode:
                valid_format = True

                if node_docstring is not None:
                    valid_format = re.match(docstring, node_docstring)

                if node_docstring is None or not valid_format:
                    self._validation_results.append(
                        _ValidationResult(
                            _ValidationType.DOCSTRING_PRESENCE
                            if node_docstring is None
                            else _ValidationType.DOCSTRING_FORMAT,
                            node.lineno,
                            node.name,
                        )
                    )

            self._function_docs.append((node.lineno, docstring))


class DocTask(Task):
    def _visit_tree(
        self,
        source: str,
        function_docs: List[Tuple[int, str]],
        validation_results: List[_ValidationResult],
        validation_mode: bool,
    ) -> bool:
        tree = None

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False

        _Visitor(source, function_docs, validation_results, validation_mode).visit(tree)

        return True

    def _add_documentation(
        self, text_stream: TextIOWrapper, validation_results: List[_ValidationResult]
    ) -> bool:
        function_docs = []
        source = text_stream.read()

        if not self._visit_tree(source, function_docs, validation_results, False):
            return False

        text_stream.seek(0)
        lines = text_stream.readlines()
        insert_offset = -1

        for start, doc in sorted(function_docs):
            position = start + insert_offset

            while position < len(lines):
                if re.match(
                    r"^.*:\s*(#.*)?(\"\"\".*)?('''.*)?$", lines[position].rstrip(),
                ):
                    lines.insert(position + 1, doc)
                    insert_offset += 1
                    break

                position += 1
            else:
                raise RuntimeError("Cannot determine function position.")

        text_stream.seek(0)
        text_stream.writelines(lines)
        text_stream.truncate()

        return True

    def _perform(
        self,
        all_files: bool = False,
        validate: bool = False,
        ignore_missing: bool = False,
    ) -> int:
        get_files_function = get_repo_files if all_files else get_changed_repo_files
        rc = ReturnCode.OK

        for path in get_files_function(
            [
                filter_python_files,
                filter_not_unit_test_files,
                filter_not_python_underscore_files,
            ]
        ):
            with open(path, "r+") as file:
                validation_results = []
                success = (
                    self._visit_tree(file.read(), [], validation_results, True)
                    if validate
                    else self._add_documentation(file, validation_results)
                )

                if not success:
                    output(f"Failed to parse Python file '{path}'.")
                    return ReturnCode.FAILED

                if ignore_missing:
                    validation_results = list(
                        filter(
                            lambda result: result.validation_type
                            != _ValidationType.DOCSTRING_PRESENCE,
                            validation_results,
                        )
                    )

                if len(validation_results) > 0:
                    rc = ReturnCode.FAILED

                    output(f"Docstring validation failed for file '{path}':")

                    for result in validation_results:
                        if result.validation_type == _ValidationType.PARAMETER:
                            output(
                                f"  - Parameter annotation for '{result.name}' "
                                f"is missing on line {result.line_number}."
                            )
                        elif result.validation_type == _ValidationType.RETURN:
                            output(
                                "  - Return annotaion is missing for function "
                                f"'{result.name}' on line {result.line_number}."
                            )
                        elif result.validation_type == _ValidationType.DOCSTRING_FORMAT:
                            output(
                                f"  - Docstring for function '{result.name}' "
                                f"on line {result.line_number} is misformatted."
                            )
                        elif (
                            result.validation_type == _ValidationType.DOCSTRING_PRESENCE
                        ):
                            output(
                                f"  - Docstring for function '{result.name}' "
                                f"on line {result.line_number} is missing."
                            )

        return rc

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = super()._add_task_parser(subparsers)
        parser.add_argument("-a", "--all", action="store_true", dest="all_files")
        parser.add_argument("-v", "--validate", action="store_true", dest="validate")
        parser.add_argument(
            "-i", "--ignore-missing", action="store_true", dest="ignore_missing"
        )

        return parser
