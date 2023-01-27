from dev.tasks.doc import DocTask
from dev.tasks.lint import LintTask
from dev.tasks.spell import SpellTask
from dev.tasks.task import Task
from dev.tasks.unused import UnusedTask


class ChainTask(Task):
    def _perform(self) -> int:
        return max(
            [
                LintTask.execute(),
                UnusedTask.execute(),
                DocTask.execute(validate=True, ignore_missing=True),
                SpellTask.execute(),
            ]
        )
