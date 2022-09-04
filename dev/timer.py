import time
from typing import Any, Callable, NamedTuple


class _TimerResult(NamedTuple):
    elasped: float
    return_value: Any


def measure_time(
    callable: Callable[..., Any], *args: Any, **kwargs: Any
) -> _TimerResult:
    start = time.monotonic()
    return_value = callable(*args, **kwargs)
    end = time.monotonic()

    return _TimerResult(end - start, return_value)
