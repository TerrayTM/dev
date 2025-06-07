from dev.linters.javascript import JavaScriptLinter


class TypeScriptLinter(JavaScriptLinter):
    @staticmethod
    def get_extension() -> str:
        return ".tsx"
