class Task:
    def perform(self) -> int:
        raise NotImplementedError()

    @classmethod
    def execute(cls) -> int:
        task = cls()

        return task.perform()
