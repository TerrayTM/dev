import ast
from functools import cache
from typing import List, NamedTuple, Optional, Union


class _Output:
    name: Optional[str] = None
    install_requires: List[str] = []


class _PackageSetupInfo(NamedTuple):
    name: Optional[str]
    install_requires: List[str]


class _Visitor(ast.NodeVisitor):
    def __init__(self, output: _Output) -> None:
        self._output = output

    def _record_install_requires(self, node: Union[ast.keyword, ast.Assign]) -> None:
        if not isinstance(node.value, ast.List):
            raise ValueError(
                "install_requires expects a list, but found " f"{type(node.value)}."
            )

        if len(self._output.install_requires) > 0:
            raise ValueError("install_requires is defined multiple times.")

        self._output.install_requires = [constant.value for constant in node.value.elts]

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "setup":
            for keyword in node.keywords:
                if keyword.arg == "name":
                    self._output.name = keyword.value.value
                elif keyword.arg == "install_requires":
                    self._record_install_requires(keyword)

    def visit_Assign(self, node: ast.Assign) -> None:
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "install_requires"
        ):
            self._record_install_requires(node)


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
