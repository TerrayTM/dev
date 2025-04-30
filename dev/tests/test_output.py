from io import StringIO
from unittest import TestCase, main

from dev.output import ConsoleColors, OutputConfig, output


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


if __name__ == "__main__":
    main()
