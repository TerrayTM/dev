import sys
from enum import Enum
from io import TextIOWrapper
from typing import TextIO


class _OutputConfig:
    stream: TextIOWrapper = sys.stdout
    disable_colors: bool = False


class ConsoleColors(Enum):
    RED = "\033[91m"
    END = "\033[0m"


def set_output_stream(stream: TextIO, disable_colors: bool = False) -> None:
    _OutputConfig.stream = stream
    _OutputConfig.disable_colors = disable_colors


def output(
    *values: object, sep: str = " ", end: str = "\n", flush: bool = False
) -> None:
    converted = []
    prepend = ""

    for value in values:
        if isinstance(value, ConsoleColors):
            if _OutputConfig.disable_colors:
                continue

            if value == ConsoleColors.END and len(converted) > 0:
                converted[-1] = f"{converted[-1]}{value.value}"
            else:
                prepend = value.value
        else:
            converted.append(f"{prepend}{str(value)}")
            prepend = ""

    print(*converted, sep=sep, end=end, file=_OutputConfig.stream, flush=flush)
