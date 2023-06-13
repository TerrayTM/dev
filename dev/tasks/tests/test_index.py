from unittest import TestCase, main

from dev.tasks.build import BuildTask
from dev.tasks.chain import ChainTask
from dev.tasks.clean import CleanTask
from dev.tasks.count import CountTask
from dev.tasks.index import get_task, get_task_map


class TestIndex(TestCase):
    def test_get_task(self) -> None:
        self.assertEqual(get_task("build"), BuildTask)
        self.assertEqual(get_task("chain"), ChainTask)
        self.assertEqual(get_task("clean"), CleanTask)
        self.assertEqual(get_task("count"), CountTask)

    def test_get_task_map(self) -> None:
        task_map = get_task_map()
        last_key = None

        for name, task in task_map.items():
            last_key = name
            self.assertEqual(name, task.task_name())

        task_map.pop(last_key)

        self.assertEqual(len(task_map) + 1, len(get_task_map()))


if __name__ == "__main__":
    main()
