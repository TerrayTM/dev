from argparse import ArgumentParser, Namespace, _SubParsersAction

from dev.constants import RC_OK
from dev.custom import CustomTask


class Task:
    def _perform(self, args: Namespace) -> int:
        raise NotImplementedError()

    @classmethod
    def _add_task_parser(cls, subparsers: _SubParsersAction) -> ArgumentParser:
        return subparsers.add_parser(cls.task_name())

    @classmethod
    def add_to_subparser(cls, subparsers: _SubParsersAction) -> None:
        cls._add_task_parser(subparsers)

    @classmethod
    def customize(cls, custom_task: CustomTask) -> None:
        cls._custom_task = custom_task

    @classmethod
    def execute(cls, args: Namespace) -> int:
        task = cls()

        if hasattr(cls, "_custom_task"):
            rc = cls._custom_task.perform_pre_step()
            if rc != RC_OK:
                return rc

        rc = task._perform(args)
        if rc != RC_OK:
            return rc

        if hasattr(cls, "_custom_task"):
            rc = cls._custom_task.perform_post_step()

        return rc

    @classmethod
    def task_name(cls) -> str:
        return cls.__name__.lower().replace("task", "")
