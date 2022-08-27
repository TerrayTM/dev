import ast
import re
from argparse import Namespace
from io import TextIOWrapper
from typing import List, NamedTuple, Optional, Tuple

from dev.constants import RC_FAILED, RC_OK
from dev.files import (filter_not_python_underscore_files,
                       filter_not_python_unit_test_files, filter_python_files,
                       get_changed_repo_files)
from dev.tasks.task import Task

SPECIAL_PARAMETER_NAMES = ("self", "cls")


class _Parameter(NamedTuple):
    name: str
    annotation: Optional[str]
    default_value: Optional[str]


def _generate_doc_string(
    parameters: List[_Parameter], return_annotation: Optional[str], space_offset: int
) -> str:
    spaces = " " * space_offset
    comment = f"\n{spaces}Placeholder function documentation string.\n"

    if len(parameters) > 0:
        comment += f"\n{spaces}Parameters\n{spaces}----------\n"

        for index, parameter in enumerate(parameters):
            default_string = (
                f" (default={str(parameter.default_value)})"
                if parameter.default_value is not None
                else ""
            )

            comment += (
                f"{spaces}{parameter.name} : "
                f"{parameter.annotation if parameter.annotation is not None else '???'}"
                f"{default_string}\n{spaces}\t"
                "Placeholder argument documentation string.\n"
            )

            if index + 1 != len(parameters):
                comment += "\n"

    if return_annotation != "None":
        comment += (
            f"\n{spaces}Returns\n{spaces}-------\n{spaces}result : "
            f"{return_annotation if return_annotation is not None else '???'}\n"
            f"{spaces}\tPlaceholder result documentation string.\n"
        )

    return f'{spaces}"""{comment}{spaces}"""\n'


class _Visitor(ast.NodeVisitor):
    def __init__(self, source: str, function_docs: List[Tuple[int, str]]) -> None:
        self._source = source
        self._function_docs = function_docs

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
                print(
                    f"Parameter annotation for '{parameter.name}' "
                    f"is missing on line {node.lineno}."
                )

        if return_annotation is None:
            print(
                "Return annotaion is missing for function "
                f"'{node.name}' on line {node.lineno}."
            )

        if ast.get_docstring(node) is None:
            self._function_docs.append(
                (
                    node.lineno,
                    _generate_doc_string(
                        parameters, return_annotation, node.col_offset + 4,
                    ),
                )
            )


class DocTask(Task):
    def _add_documentation(self, text_stream: TextIOWrapper) -> bool:
        function_docs = []
        source = text_stream.read()
        tree = None

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return False

        _Visitor(source, function_docs).visit(tree)

        text_stream.seek(0)
        lines = text_stream.readlines()
        insert_offset = -1

        for start, doc in sorted(function_docs):
            position = start + insert_offset

            while position < len(lines):
                if re.match(
                    "^.*:\s*(#.*)?(\"\"\".*)?('''.*)?$", lines[position].rstrip(),
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

    def _perform(self, _: Namespace) -> int:
        for path in get_changed_repo_files(
            [
                filter_python_files,
                filter_not_python_unit_test_files,
                filter_not_python_underscore_files,
            ]
        ):
            with open(path, "r+") as file:
                if not self._add_documentation(file):
                    print(f"Failed to parse Python file '{path}'.")
                    return RC_FAILED

        return RC_OK
