from argparse import ArgumentParser, Namespace, _SubParsersAction


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
    def execute(cls, args: Namespace) -> int:
        task = cls()

        return task._perform(args)

    @classmethod
    def task_name(cls) -> str:
        return cls.__name__.lower().replace("task", "")
