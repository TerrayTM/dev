CONFIG_FILE = "dev.yaml"
SECRET_CONFIG_FILE = "dev.secret.yaml"
SETUP_FILE = "setup.py"
CODE_EXTENSIONS = (".py", ".js", ".css", ".html", ".php", ".cs", ".tsx", ".ts")


class ReturnCode:
    OK: int = 0
    FAILED: int = 1
    INTERRUPTED: int = 2
