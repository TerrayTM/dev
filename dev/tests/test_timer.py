import time
from unittest import TestCase, main

from dev.timer import measure_time


def _add(a: int, b: int) -> int:
    return a + b


def _raise_value_error() -> None:
    raise ValueError()


def _sleep_briefly() -> None:
    time.sleep(0.1)


class TestMeasureTime(TestCase):
    def test_return_value(self) -> None:
        result = measure_time(lambda: 42)
        self.assertEqual(result.return_value, 42)

    def test_elapsed_measures_duration(self) -> None:
        result = measure_time(_sleep_briefly)
        self.assertGreaterEqual(result.elapsed, 0.01)

    def test_no_exception_on_success(self) -> None:
        result = measure_time(lambda: 42)
        self.assertIsNone(result.exception)

    def test_captures_exception(self) -> None:
        result = measure_time(_raise_value_error)
        self.assertIsNone(result.return_value)
        self.assertIsInstance(result.exception, ValueError)

    def test_raise_exception_flag(self) -> None:
        with self.assertRaises(ValueError):
            measure_time(_raise_value_error, raise_exception=True)

    def test_passes_positional_args(self) -> None:
        result = measure_time(_add, 3, 4)
        self.assertEqual(result.return_value, 7)

    def test_passes_keyword_args(self) -> None:
        result = measure_time(_add, a=10, b=5)
        self.assertEqual(result.return_value, 15)


if __name__ == "__main__":
    main()
