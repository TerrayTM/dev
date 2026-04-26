import sys
from contextlib import contextmanager
from contextvars import ContextVar
from enum import Enum
from typing import Generator, List, Optional, TextIO

_stream: ContextVar[TextIO] = ContextVar("stream", default=sys.stdout)
_disable_colors: ContextVar[bool] = ContextVar("disable_colors", default=False)


class _OutputConfig:
    @property
    def stream(self) -> TextIO:
        return _stream.get()

    @stream.setter
    def stream(self, value: TextIO) -> None:
        _stream.set(value)

    @property
    def disable_colors(self) -> bool:
        return _disable_colors.get()

    @disable_colors.setter
    def disable_colors(self, value: bool) -> None:
        _disable_colors.set(value)


OutputConfig = _OutputConfig()


class ConsoleColors(Enum):
    RED = "\033[91m"
    END = "\033[0m"


@contextmanager
def output_config(
    stream: Optional[TextIO] = None, disable_colors: Optional[bool] = None
) -> Generator[None, None, None]:
    stream_token = _stream.set(stream if stream is not None else _stream.get())
    colors_token = _disable_colors.set(
        disable_colors if disable_colors is not None else _disable_colors.get()
    )
    try:
        yield
    finally:
        _stream.reset(stream_token)
        _disable_colors.reset(colors_token)


def is_using_stdout() -> bool:
    return _stream.get() == sys.stdout or "<stdout>" in str(_stream.get())


def output(
    *values: object, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    converted: List[str] = []
    prepend = ""

    for value in values:
        if isinstance(value, ConsoleColors):
            if _disable_colors.get():
                continue

            if value == ConsoleColors.END and len(converted) > 0:
                converted[-1] = f"{converted[-1]}{value.value}"
            else:
                prepend = value.value
        else:
            converted.append(f"{prepend}{str(value)}")
            prepend = ""

    print(*converted, sep=sep, end=end, file=_stream.get(), flush=flush)
