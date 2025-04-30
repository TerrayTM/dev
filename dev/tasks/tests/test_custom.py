from io import StringIO
from typing import List
from unittest import TestCase, main

from dev.constants import ReturnCode
from dev.loader import load_tasks_from_config
from dev.output import OutputConfig
from dev.tasks.custom import CustomTask


class TestCustom(TestCase):
    def _get_custom_tasks(self, run_parallel: bool = False) -> List[CustomTask]:
        return load_tasks_from_config(
            {},
            config={
                "variables": {"EXECUTOR": "python"},
                "tasks": {
                    "echo": {
                        "pre": ["{EXECUTOR} -c \"import os; print('A')\""],
                        "run": [
                            "{EXECUTOR} -c \"import os; print(os.environ['VAR_A'])\"",
                            '{EXECUTOR} -c "import os; import time; time.sleep(0.1); '
                            "print(os.environ['VAR_B'])\"",
                            "{EXECUTOR} -c \"import os; print(os.environ['VAR_C'])\"",
                        ],
                        "post": ["{EXECUTOR} -c \"import os; print('A')\""],
                        "env": ["VAR_A", "VAR_B", "VAR_C"],
                        **({"parallel": True} if run_parallel else {}),
                    }
                },
            },
            secret_config={"variables": {"VAR_A": 1, "VAR_B": 2, "VAR_C": 3}},
        )

    def test_custom_task(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        custom_tasks = self._get_custom_tasks()

        self.assertEqual(len(custom_tasks), 1)

        custom_task, *_ = custom_tasks
        rc = custom_task.execute()

        self.assertEqual(rc, ReturnCode.OK)
        self.assertEqual(stream.getvalue(), "A\n1\n2\n3\nA\n")

    def test_custom_task_parallel(self) -> None:
        stream = StringIO()
        OutputConfig.stream = stream

        custom_tasks = self._get_custom_tasks(run_parallel=True)

        self.assertEqual(len(custom_tasks), 1)

        custom_task, *_ = custom_tasks
        rc = custom_task.execute()
        value = stream.getvalue()

        self.assertEqual(rc, ReturnCode.OK)
        self.assertEqual(value[:2], "A\n")
        self.assertEqual(value[-2:], "A\n")
        self.assertEqual(set(value[2:-2].strip().split("\n")), {"1", "2", "3"})


if __name__ == "__main__":
    main()
