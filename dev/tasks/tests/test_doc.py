from io import StringIO
from unittest import TestCase, main

from dev.tasks.doc import DocTask

test_case = '''
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Union

Vector = Union[List[int], Tuple[int, ...]]


def f1() -> None:
    pass


def f2(a: Vector) -> int:
    pass


def f3(a: int, b: Union[str, List[float]]) -> str:
    pass


def f4(a: Callable[[int, str], float], b: str, c: Dict[str, int]) -> Iterable[int]:
    pass


def f5(a: Callable[..., Any], b: Set[int], c: Tuple[int, int]) -> None:
    pass


def f6(
    a: str,
    b: str,
    c: str,
) -> int: # Function
    pass


def f7(a: int = 5, b: str = "default", c: List[int] = [1, 2, 3]) -> "f7":
    pass


def decorator(function: Any) -> Any:
    return function


class A:
    @classmethod
    def a1(self, p: str) -> Any:
        pass

    @decorator
    @decorator
    @decorator
    def a2(self, p: str) -> Any:
        pass

    class B:
        def b1(self, p: "AType") -> "BType":
            pass

        class C:
            @classmethod
            def c1(self, p: str) -> Any:
                pass

            @classmethod
            def c2(self, p: ModuleType) -> Any:
                pass

        class D:
            @classmethod
            def d1(self, p: str) -> Any:
                pass

            @decorator
            def d2(self, p: str) -> Any:
                pass

    class E:
        def e(self, p: str) -> Any:
            pass


@decorator
def nested(a: A) -> None:
    def inner() -> None:
        def innermost() -> None:
            pass


def documented() -> None:
    """
    Documentation
    """
'''

expected_result = '''
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Union

Vector = Union[List[int], Tuple[int, ...]]


def f1() -> None:
    """
    Placeholder function documentation string.
    """
    pass


def f2(a: Vector) -> int:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : Vector
        Placeholder argument documentation string.

    Returns
    -------
    result : int
        Placeholder result documentation string.
    """
    pass


def f3(a: int, b: Union[str, List[float]]) -> str:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : int
        Placeholder argument documentation string.

    b : Union[str, List[float]]
        Placeholder argument documentation string.

    Returns
    -------
    result : str
        Placeholder result documentation string.
    """
    pass


def f4(a: Callable[[int, str], float], b: str, c: Dict[str, int]) -> Iterable[int]:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : Callable[[int, str], float]
        Placeholder argument documentation string.

    b : str
        Placeholder argument documentation string.

    c : Dict[str, int]
        Placeholder argument documentation string.

    Returns
    -------
    result : Iterable[int]
        Placeholder result documentation string.
    """
    pass


def f5(a: Callable[..., Any], b: Set[int], c: Tuple[int, int]) -> None:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : Callable[..., Any]
        Placeholder argument documentation string.

    b : Set[int]
        Placeholder argument documentation string.

    c : Tuple[int, int]
        Placeholder argument documentation string.
    """
    pass


def f6(
    a: str,
    b: str,
    c: str,
) -> int: # Function
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : str
        Placeholder argument documentation string.

    b : str
        Placeholder argument documentation string.

    c : str
        Placeholder argument documentation string.

    Returns
    -------
    result : int
        Placeholder result documentation string.
    """
    pass


def f7(a: int = 5, b: str = "default", c: List[int] = [1, 2, 3]) -> "f7":
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : int (default=5)
        Placeholder argument documentation string.

    b : str (default="default")
        Placeholder argument documentation string.

    c : List[int] (default=[1, 2, 3])
        Placeholder argument documentation string.

    Returns
    -------
    result : f7
        Placeholder result documentation string.
    """
    pass


def decorator(function: Any) -> Any:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    function : Any
        Placeholder argument documentation string.

    Returns
    -------
    result : Any
        Placeholder result documentation string.
    """
    return function


class A:
    @classmethod
    def a1(self, p: str) -> Any:
        """
        Placeholder function documentation string.

        Parameters
        ----------
        p : str
            Placeholder argument documentation string.

        Returns
        -------
        result : Any
            Placeholder result documentation string.
        """
        pass

    @decorator
    @decorator
    @decorator
    def a2(self, p: str) -> Any:
        """
        Placeholder function documentation string.

        Parameters
        ----------
        p : str
            Placeholder argument documentation string.

        Returns
        -------
        result : Any
            Placeholder result documentation string.
        """
        pass

    class B:
        def b1(self, p: "AType") -> "BType":
            """
            Placeholder function documentation string.

            Parameters
            ----------
            p : AType
                Placeholder argument documentation string.

            Returns
            -------
            result : BType
                Placeholder result documentation string.
            """
            pass

        class C:
            @classmethod
            def c1(self, p: str) -> Any:
                """
                Placeholder function documentation string.

                Parameters
                ----------
                p : str
                    Placeholder argument documentation string.

                Returns
                -------
                result : Any
                    Placeholder result documentation string.
                """
                pass

            @classmethod
            def c2(self, p: ModuleType) -> Any:
                """
                Placeholder function documentation string.

                Parameters
                ----------
                p : ModuleType
                    Placeholder argument documentation string.

                Returns
                -------
                result : Any
                    Placeholder result documentation string.
                """
                pass

        class D:
            @classmethod
            def d1(self, p: str) -> Any:
                """
                Placeholder function documentation string.

                Parameters
                ----------
                p : str
                    Placeholder argument documentation string.

                Returns
                -------
                result : Any
                    Placeholder result documentation string.
                """
                pass

            @decorator
            def d2(self, p: str) -> Any:
                """
                Placeholder function documentation string.

                Parameters
                ----------
                p : str
                    Placeholder argument documentation string.

                Returns
                -------
                result : Any
                    Placeholder result documentation string.
                """
                pass

    class E:
        def e(self, p: str) -> Any:
            """
            Placeholder function documentation string.

            Parameters
            ----------
            p : str
                Placeholder argument documentation string.

            Returns
            -------
            result : Any
                Placeholder result documentation string.
            """
            pass


@decorator
def nested(a: A) -> None:
    """
    Placeholder function documentation string.

    Parameters
    ----------
    a : A
        Placeholder argument documentation string.
    """
    def inner() -> None:
        def innermost() -> None:
            pass


def documented() -> None:
    """
    Documentation
    """
'''


class TestDoc(TestCase):
    def setUp(self) -> None:
        class MockDocTask(DocTask):
            def add_documentation(self, text_stream):
                return self._add_documentation(text_stream, [])

        self._doc_task = MockDocTask()

    def test_documentation(self) -> None:
        stream = StringIO(test_case)
        success = self._doc_task.add_documentation(stream)
        stream.seek(0)
        result = stream.read()

        self.assertTrue(success)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    main()
