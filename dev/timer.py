import time
from typing import Any, Callable, NamedTuple, Optional


class _TimerResult(NamedTuple):
    elasped: float
    return_value: Any
    exception: Optional[Exception]


def measure_time(
    callable: Callable[..., Any],
    *args: Any,
    raise_exception: bool = False,
    **kwargs: Any,
) -> _TimerResult:
    return_value = None
    exception = None
    start = time.monotonic()

    try:
        return_value = callable(*args, **kwargs)
    except Exception as error:
        if raise_exception:
            raise error
        exception = error

    return _TimerResult(time.monotonic() - start, return_value, exception)
