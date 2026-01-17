import subprocess
from typing import Any, Dict, List, Optional

from dev.output import is_using_stdout, output


def run_process(
    command: List[str],
    check_call: bool = False,
    shell: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> subprocess.CompletedProcess[str]:
    is_stdout = is_using_stdout()
    kwargs: dict[str, Any] = (
        {} if is_stdout else {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
    )
    result = subprocess.run(command, encoding="utf8", shell=shell, env=env, **kwargs)

    if not is_stdout:
        if result.stdout:
            output(result.stdout.strip())

        if result.stderr:
            output(result.stderr.strip())

    if check_call:
        result.check_returncode()

    return result
