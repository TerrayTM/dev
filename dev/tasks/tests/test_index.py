from unittest import TestCase, main

from dev.tasks.build import BuildTask
from dev.tasks.chain import ChainTask
from dev.tasks.clean import CleanTask
from dev.tasks.count import CountTask
from dev.tasks.doc import DocTask
from dev.tasks.index import get_task, get_task_map
from dev.tasks.install import InstallTask
from dev.tasks.lint import LintTask
from dev.tasks.publish import PublishTask
from dev.tasks.run import RunTask
from dev.tasks.spell import SpellTask
from dev.tasks.test import TestTask
from dev.tasks.time import TimeTask
from dev.tasks.uninstall import UninstallTask
from dev.tasks.unused import UnusedTask


class TestIndex(TestCase):
    def test_get_task(self) -> None:
        self.assertEqual(get_task("build"), BuildTask)
        self.assertEqual(get_task("clean"), CleanTask)
        self.assertEqual(get_task("count"), CountTask)
        self.assertEqual(get_task("doc"), DocTask)
        self.assertEqual(get_task("install"), InstallTask)
        self.assertEqual(get_task("lint"), LintTask)
        self.assertEqual(get_task("publish"), PublishTask)
        self.assertEqual(get_task("run"), RunTask)
        self.assertEqual(get_task("test"), TestTask)
        self.assertEqual(get_task("uninstall"), UninstallTask)
        self.assertEqual(get_task("time"), TimeTask)
        self.assertEqual(get_task("spell"), SpellTask)
        self.assertEqual(get_task("chain"), ChainTask)
        self.assertEqual(get_task("unused"), UnusedTask)

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
