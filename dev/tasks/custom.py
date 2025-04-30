import multiprocessing
import os
import shlex
import subprocess
from argparse import Namespace, _SubParsersAction
from functools import cache, partial
from io import StringIO
from queue import Empty
from typing import Any, Callable, Dict, List, Optional, Union

from dev.constants import ReturnCode
from dev.exceptions import TaskArgumentError, TaskNotFoundError
from dev.output import OutputConfig, is_using_stdout, output
from dev.process import run_process

_DEV_PREFIX = "dev:"


def _execute_function(
    function_source: Callable[[], Union[int, subprocess.CompletedProcess]],
    output_queue: Optional[multiprocessing.Queue],
    disable_colors: bool,
) -> None:
    OutputConfig.disable_colors = disable_colors

    stream = None
    if output_queue is not None:
        stream = StringIO()
        OutputConfig.stream = stream

    try:
        result = function_source()

        if stream is not None and output_queue is not None:
            output_queue.put(stream.getvalue())

        if isinstance(result, int):
            raise SystemExit(result)
        raise SystemExit(result.returncode)
    except KeyboardInterrupt:
        raise SystemExit(ReturnCode.INTERRUPTED)
    except Exception:
        raise SystemExit(ReturnCode.FAILED)


class CustomTask:
    def __init__(
        self,
        name: str,
        run: Optional[List[str]],
        pre_step: Optional[List[str]],
        post_step: Optional[List[str]],
        run_parallel: bool,
        dynamic_task_map: Dict[str, Any],
        env: Optional[Dict[str, str]],
    ) -> None:
        self._name = name
        self._run = run
        self._pre_step = pre_step
        self._post_step = post_step
        self._run_parallel = run_parallel
        self._dynamic_task_map = dynamic_task_map
        self._env = env

    @cache
    def _parse_task(self, line: str) -> Any:
        name = line[len(_DEV_PREFIX) :]
        if name not in self._dynamic_task_map:
            raise TaskNotFoundError(f"'{name}' task cannot be found.")

        return self._dynamic_task_map[name]

    def _run_command(self, command: Optional[List[str]]) -> int:
        rc = ReturnCode.OK
        if command is not None:
            env_vars = None if self._env is None else {**os.environ, **self._env}
            if self._run_parallel:
                processes = []
                output_queue = None if is_using_stdout() else multiprocessing.Queue()
                try:
                    for entry in command:
                        function_source = (
                            self._parse_task(entry).execute
                            if entry.startswith(_DEV_PREFIX)
                            else partial(
                                run_process,
                                shlex.split(entry),
                                shell=True,
                                env=env_vars,
                            )
                        )
                        process = multiprocessing.Process(
                            target=_execute_function,
                            args=(
                                function_source,
                                output_queue,
                                OutputConfig.disable_colors,
                            ),
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

                    rc = ReturnCode.INTERRUPTED

                if output_queue is not None:
                    while True:
                        try:
                            output(output_queue.get(block=False), end="")
                        except Empty:
                            break
            else:
                try:
                    for entry in command:
                        if entry.startswith(_DEV_PREFIX):
                            rc = self._parse_task(entry).execute()
                        else:
                            rc = run_process(
                                shlex.split(entry), shell=True, env=env_vars
                            ).returncode

                        if rc != ReturnCode.OK:
                            return rc
                except KeyboardInterrupt:
                    return ReturnCode.INTERRUPTED

        return rc

    def validate(self) -> None:
        for line in (
            (self._pre_step or []) + (self._run or []) + (self._post_step or [])
        ):
            if line.startswith(_DEV_PREFIX):
                self._parse_task(line)

    def override_existing(self) -> bool:
        return self._run is not None

    def perform_pre_step(self) -> int:
        return self._run_command(self._pre_step)

    def perform_post_step(self) -> int:
        return self._run_command(self._post_step)

    def add_to_subparser(self, subparsers: _SubParsersAction) -> None:
        subparsers.add_parser(self._name)

    def execute(
        self,
        args: Optional[Namespace] = None,
        allow_extraneous_args: bool = False,
        **kwargs: Any,
    ) -> int:
        if not allow_extraneous_args:
            arg_count = 0 if args is None else len(vars(args))
            arg_count += len(kwargs)

            if arg_count > 0:
                raise TaskArgumentError("Cannot pass arguments to a custom task.")

        rc = self.perform_pre_step()
        if rc != ReturnCode.OK:
            return rc

        rc = self._run_command(self._run)
        if rc != ReturnCode.OK:
            return rc

        return self.perform_post_step()

    def task_name(self) -> str:
        return self._name
