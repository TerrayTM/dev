from abc import ABC, abstractmethod
from typing import Iterable, List, Set


class BaseLinter(ABC):
    @staticmethod
    @abstractmethod
    def _get_comment() -> str:
        pass

    @classmethod
    @abstractmethod
    def _validate(
        cls, file: str, line_length: int, line: str, line_number: int
    ) -> bool:
        pass

    @classmethod
    @abstractmethod
    def _format(
        cls, files: Iterable[str], line_length: int, validate: bool
    ) -> Set[str]:
        pass

    @classmethod
    def format(
        cls, unfiltered_files: Iterable[str], line_length: int, validate: bool
    ) -> Set[str]:
        target_files = [
            file
            for file in unfiltered_files
            if any(file.endswith(extension) for extension in cls.get_extensions())
        ]

        if not target_files:
            return set()

        formatted = cls._format(target_files, line_length, validate)

        for file in target_files:
            is_valid = True

            with open(file, encoding="utf8") as reader:
                for line_number, line in enumerate(reader, 1):
                    line = line.rstrip("\n")

                    if not line.endswith(f"{cls._get_comment()} dev-star ignore"):
                        is_valid &= cls._validate(file, line_length, line, line_number)

            if not is_valid and validate:
                formatted.add(file)

        return formatted

    @staticmethod
    @abstractmethod
    def get_install() -> str:
        pass

    @staticmethod
    @abstractmethod
    def get_extensions() -> List[str]:
        pass

    @staticmethod
    @abstractmethod
    def get_width() -> int:
        pass
