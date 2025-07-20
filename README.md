# dev
Dev tools CLI for performing common development tasks.

<a href="https://pypi.org/project/dev-star/"><img alt="PyPI" src="https://img.shields.io/pypi/v/dev-star?color=green&label=PyPI%20Package"></a>
<a href="https://opensource.org/licenses/Apache-2.0"><img alt="Apache" src="https://img.shields.io/badge/License-Apache%202.0-blue.svg"></a>
<img alt="Build" src="https://terrytm.com/api/wain.php?route=badge&name=dev">

## Commands
### `dev build`
- This command handles building and validating a Python package. It ensures a clean environment, creates the package, and verifies its integrity.

### `dev chain`
- This command runs a series of code quality and documentation checks. It returns the highest status code among them, indicating the most severe result.

### `dev clean`
- This command removes Python cache files and `__pycache__` directories to clean the project. It ensures a fresh state for the codebase.

### `dev count`
- This command counts lines of code in a project, optionally grouped by author, excluding tests, or showing detailed output. It can operate across all files or use `git` to break down contributions by individual authors.

### `dev doc`
- This command generates docstrings for all functions and validates them to ensure they match the function signatures. It also checks that all functions are properly type-annotated.

### `dev install`
- This command installs the Python package locally by executing the setup script. It makes the package available in the current environment for development and testing.

### `dev lint`
- This command runs linters on modified files by default, with the option to lint all files or specific paths. It supports multiple languages including Python, JavaScript, and TypeScript.

### `dev publish`
- This command publishes the built package in the `dist` directory to PyPI using Twine. It assumes the distribution artifacts have already been built.

### `dev run`
- This command runs the Python program defined at the `main.py` entry point. It acts as a convenient shortcut for launching the application.

### `dev spell`
- This command checks spelling across project files. It helps maintain consistency and catch common typos in code, comments, and documentation.

### `dev time`
- This command measures how long a command takes to run, repeating it multiple times and reporting the fastest execution time. It's useful for benchmarking performance of shell commands.

### `dev test`
- This command runs unit tests in a Python project. It can either use Python's `unittest` discovery or manually execute test files in parallel, optionally filtering them. It reports results, tracks failures, and summarizes execution time.

### `dev uninstall`
- This command uninstalls a Python package by reading its setup file to determine the package name, then running `pip uninstall` and cleaning up related metadata. It ensures the package and its build info are fully removed.

### `dev unused`
- This command runs `pylint` on changed Python files to check for unused imports. It also can filter the files based on input options and report any issues found.

### `dev env`
- This command executes a given shell command with all configuration variables exported as environment variables. It simplifies running tools or scripts that depend on settings defined in the `dev.yaml` file.
