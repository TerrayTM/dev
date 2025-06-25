from typing import List

from dev.linters.javascript import JavaScriptLinter


class TypeScriptLinter(JavaScriptLinter):
    @staticmethod
    def get_extensions() -> List[str]:
        return [".tsx", ".ts"]
