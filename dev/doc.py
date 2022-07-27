import ast
import importlib.util
import inspect
import os
import re
import subprocess
from argparse import Namespace
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Type, Union

from dev.constants import RC_OK
from dev.task import Task


def _get_function_id(function_name: str, line_number: int) -> str:
    return f"{function_name}:{line_number}"


class _Visitor(ast.NodeVisitor):
    def __init__(
        self, function_locations: List[Tuple[int, str]], offset_map: Dict[int, int]
    ) -> None:
        self._function_locations = function_locations
        self._offset_map = offset_map

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if ast.get_docstring(node) is None:
            function_id = _get_function_id(node.name, node.lineno)
            self._function_locations.append((function_id, node.lineno))
            self._offset_map[function_id] = node.col_offset + 4


class DocTask(Task):
    def _format_annotation(self, annotation: Any) -> str:
        if annotation is inspect.Signature.empty:
            return "???"

        return (
            str(annotation).split(".")[-1].rstrip("'>")
            if "." in str(annotation)
            else annotation.__name__
        )

    def _generate_doc_string(
        self, function_object: Callable[..., Any], space_offset: int
    ) -> str:
        spaces = " " * space_offset
        comment = f"\n{spaces}Placeholder function documentation string.\n"
        signature = inspect.signature(function_object)
        line = function_object.__code__.co_firstlineno

        if len(signature.parameters) > 0:
            comment += f"\n{spaces}Parameters\n{spaces}----------\n"

            for index, item in enumerate(signature.parameters.items()):
                name, parameter = item

                if name == "self":
                    continue

                default_string = (
                    f" (default={str(parameter.default)})"
                    if parameter.default is not inspect.Signature.empty
                    else ""
                )

                if parameter.annotation is inspect.Signature.empty:
                    print(
                        f"Parameter '{name}' is not annotated on function line {line}."
                    )

                comment += (
                    f"{spaces}{name} : "
                    f"{self._format_annotation(parameter.annotation)}"
                    f"{default_string}\n{spaces}\t"
                    "Placeholder argument documentation string.\n"
                )

                if index + 1 != len(signature.parameters):
                    comment += "\n"

        if signature.return_annotation is inspect.Signature.empty:
            print(f"Return is not annotated on function line {line}.")

        if (
            signature.return_annotation is not None
            or signature.return_annotation is inspect.Signature.empty
        ):
            comment += (
                f"\n{spaces}Returns\n{spaces}-------\n{spaces}result : "
                f"{self._format_annotation(signature.return_annotation)}\n"
                f"{spaces}\tPlaceholder result documentation string.\n"
            )

        return f'{spaces}"""{comment}{spaces}"""\n'

    def _get_functions_from_target(
        self, target: Union[ModuleType, Type], function_ids: Set[str]
    ) -> List[Tuple[str, Callable[..., Any]]]:
        functions = []

        for function_name, function_object in inspect.getmembers(
            target, inspect.isfunction
        ):
            function_id = _get_function_id(
                function_name, function_object.__code__.co_firstlineno
            )

            if function_id in function_ids:
                functions.append((function_id, function_object))

        return functions

    def _discover_functions(
        self, path: str, function_ids: Set[str]
    ) -> List[Tuple[str, Callable[..., Any]]]:
        class_functions = []
        spec = importlib.util.spec_from_file_location("MODULE", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for _, class_object in inspect.getmembers(module, predicate=inspect.isclass):
            class_functions.extend(
                self._get_functions_from_target(class_object, function_ids)
            )

        return class_functions + self._get_functions_from_target(module, function_ids)

    def _discover_files(self) -> Iterable[str]:
        return filter(
            lambda file: file
            and file.endswith(".py")
            and not os.path.basename(file).startswith("test_")
            and not re.match("^.*__.*__\.py$", file),
            subprocess.check_output(["git", "ls-files"]).decode("utf-8").split("\n"),
        )

    def _perform(self, _: Namespace) -> int:
        for path in self._discover_files():
            with open(path, "r+") as file:
                offset_map = {}
                function_locations = []
                tree = ast.parse(file.read())
                _Visitor(function_locations, offset_map).visit(tree)

                doc_string_map = {
                    function_name: self._generate_doc_string(
                        callable_object, offset_map[function_name]
                    )
                    for function_name, callable_object in self._discover_functions(
                        path, set(offset_map.keys())
                    )
                }

                file.seek(0)
                lines = file.readlines()
                insert_offset = -1

                for name, start in sorted(
                    function_locations, key=lambda entry: entry[1]
                ):
                    position = start + insert_offset

                    while position < len(lines):
                        if re.match(
                            "^.*:\s*(#.*)?(\"\"\".*)?('''.*)?$",
                            lines[position].rstrip(),
                        ):
                            lines.insert(position + 1, doc_string_map[name])
                            insert_offset += 1
                            break

                        position += 1
                    else:
                        raise RuntimeError("Cannot determine function position.")

                file.seek(0)
                file.writelines(lines)
                file.truncate()

        return RC_OK
