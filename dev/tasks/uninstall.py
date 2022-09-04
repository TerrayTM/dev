import ast
import os
import shutil
import subprocess
from typing import Optional

from dev.constants import ReturnCode
from dev.output import output
from dev.tasks.task import Task


class _PackageName:
    name: Optional[str] = None


class _Visitor(ast.NodeVisitor):
    def __init__(self, package_name: _PackageName) -> None:
        self._package_name = package_name

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id == "setup":
            for keyword in node.keywords:
                if keyword.arg == "name":
                    self._package_name.name = keyword.value.value


class UninstallTask(Task):
    def _perform(self) -> int:
        if not os.path.isfile("setup.py"):
            output("Cannot find setup file.")
            return ReturnCode.FAILED

        data = None
        package_name = _PackageName()

        with open("setup.py") as file:
            data = file.read()

        try:
            _Visitor(package_name).visit(ast.parse(data))
        except SyntaxError:
            output("Failed to parse setup file.")
            return ReturnCode.FAILED

        if package_name.name is None:
            output("Failed to determine package name from setup file.")
            return ReturnCode.FAILED

        subprocess.check_call(["pip", "uninstall", "-y", package_name.name])

        egg_folder = f"{package_name.name.replace('-', '_')}.egg-info"
        if os.path.isdir(egg_folder):
            shutil.rmtree(egg_folder)

        return ReturnCode.OK
