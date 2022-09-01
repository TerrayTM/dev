import sys
from io import TextIOWrapper
from typing import TextIO


class _OutputConfig:
    stream: TextIOWrapper = sys.stdout


def set_output_stream(stream: TextIO) -> None:
    _OutputConfig.stream = stream


def output(*values: object) -> None:
    print(*values, file=_OutputConfig.stream)
