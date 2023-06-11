import multiprocessing
import os
from argparse import Namespace
from typing import Any, List, Optional

from dev.constants import ReturnCode


def _execute_line(line: str) -> None:
    try:
        raise SystemExit(os.system(line))
    except KeyboardInterrupt:
        raise SystemExit(ReturnCode.INTERRUPTED)


class CustomTask:
    def __init__(
        self,
        run: Optional[List[str]],
        pre_step: Optional[List[str]],
        post_step: Optional[List[str]],
        run_parallel: bool,
    ) -> None:
        self._run = run
        self._pre_step = pre_step
        self._post_step = post_step
        self._run_parallel = run_parallel

    def _run_command(self, command: Optional[List[str]]) -> int:
        rc = ReturnCode.OK
        if command is not None:
            if self._run_parallel:
                processes = []
                try:
                    for entry in command:
                        process = multiprocessing.Process(
                            target=_execute_line, args=(entry,)  # dev-star ignore
                        )
                        processes.append(process)
                        process.start()

                    for process in processes:
                        process.join()

                        if process.exitcode != ReturnCode.OK:
                            rc = process.exitcode
                except KeyboardInterrupt:
                    for process in processes:
                        if process.is_alive():
                            process.terminate()
                            process.join()

                    return ReturnCode.INTERRUPTED
            else:
                try:
                    for entry in command:
                        rc = os.system(entry)
                        if rc != ReturnCode.OK:
                            return rc
                except KeyboardInterrupt:
                    return ReturnCode.INTERRUPTED

        return rc

    def override_existing(self) -> bool:
        return self._run is not None

    def perform_pre_step(self) -> int:
        return self._run_command(self._pre_step)

    def perform_post_step(self) -> int:
        return self._run_command(self._post_step)

    def execute(self, _: Optional[Namespace], **kwargs: Any) -> int:
        rc = self.perform_pre_step()
        if rc != ReturnCode.OK:
            return rc

        rc = self._run_command(self._run)
        if rc != ReturnCode.OK:
            return rc

        return self.perform_post_step()
