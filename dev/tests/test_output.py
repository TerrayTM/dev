import sys
from io import StringIO
from unittest import TestCase, main

from dev.output import (
    ConsoleColors,
    OutputConfig,
    is_using_stdout,
    output,
    output_config,
)


class TestOutput(TestCase):
    def test_output(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream
        OutputConfig.disable_colors = True

        output("A", "B", "C")
        output()
        output(ConsoleColors.RED, "W", ConsoleColors.END)
        output(TestCase)

        self.assertEqual(
            stream.getvalue(), "A B C\n\nW\n<class 'unittest.case.TestCase'>\n"
        )

    def test_colors(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        output("A", ConsoleColors.RED, "B", "C", ConsoleColors.END, "D", "E", sep="|")
        output(ConsoleColors.RED, "B", ConsoleColors.END, sep="|")
        output(ConsoleColors.RED, ConsoleColors.END, sep="|")

        self.assertEqual(
            stream.getvalue(), "A|\033[91mB|C\033[0m|D|E\n\033[91mB\033[0m\n\n"
        )

    def test_is_using_stdout(self) -> None:
        with output_config(stream=sys.stdout):
            self.assertTrue(is_using_stdout())

        stream = StringIO()
        with output_config(stream=stream):
            self.assertFalse(is_using_stdout())

    def test_output_config(self) -> None:
        outer = StringIO()
        inner = StringIO()

        with output_config(stream=outer, disable_colors=True):
            output("outer")
            with output_config(stream=inner, disable_colors=False):
                output(ConsoleColors.RED, "inner", ConsoleColors.END)
            output("outer")

        self.assertEqual(outer.getvalue(), "outer\nouter\n")
        self.assertEqual(inner.getvalue(), "\033[91minner\033[0m\n")


if __name__ == "__main__":
    main()
