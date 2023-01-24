import subprocess
from typing import List

from dev.output import is_using_stdout, output


def subprocess_run(
    command: List[str], check_call: bool = False, shell: bool = False
) -> subprocess.CompletedProcess:
    is_stdout = is_using_stdout()
    kwargs = {} if is_stdout else {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    result = subprocess.run(command, encoding="utf8", shell=shell, **kwargs)

    if not is_stdout:
        if result.stdout:
            output(result.stdout)

        if result.stderr:
            output(result.stderr)

    if check_call and result.returncode:
        raise subprocess.CalledProcessError(result.returncode, command)

    return result
