import ast
from functools import cache
from typing import List, NamedTuple, Optional


class _Output:
    name: Optional[str] = None
    install_requires: List[str] = []


class _PackageSetupInfo(NamedTuple):
    name: Optional[str]
    install_requires: List[str]


class _Visitor(ast.NodeVisitor):
    def __init__(self, output: _Output) -> None:
        self._output = output

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "setup":
            for keyword in node.keywords:
                if keyword.arg == "name":
                    self._output.name = keyword.value.value
                elif keyword.arg == "install_requires":
                    if not isinstance(keyword.value, ast.List):
                        raise ValueError(
                            "install_requires expects a list, but found "
                            f"{type(keyword.value)}."
                        )

                    self._output.install_requires = [
                        constant.value for constant in keyword.value.elts
                    ]


@cache
def parse_setup_file(path: str) -> Optional[_PackageSetupInfo]:
    data = None
    output = _Output()

    with open(path) as file:
        data = file.read()

    try:
        _Visitor(output).visit(ast.parse(data))
    except SyntaxError:
        return None

    return _PackageSetupInfo(output.name, output.install_requires)
