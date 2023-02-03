CONFIG_FILE = "dev.yaml"
SETUP_FILE = "setup.py"
CODE_EXTENSIONS = (".py", ".js", ".css", ".html", ".php", ".cs")


class ReturnCode:
    OK: int = 0
    FAILED: int = 1
    INTERRUPTED: int = 2
