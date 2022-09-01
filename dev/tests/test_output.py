from io import StringIO
from unittest import TestCase, main

from dev.output import output, set_output_stream


class TestOutput(TestCase):
    def test_output(self):
        stream = StringIO()
        set_output_stream(stream)

        output("A", "B", "C")
        output()
        output(TestCase)

        self.assertEqual(
            stream.getvalue(), "A B C\n\n<class 'unittest.case.TestCase'>\n"
        )


if __name__ == "__main__":
    main()
