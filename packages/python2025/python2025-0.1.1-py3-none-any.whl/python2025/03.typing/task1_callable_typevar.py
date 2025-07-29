# ruff: noqa: E501
# есть функция-процессор process, которая принимает первым аргументом функцию func
# и вторым аргументом - итерируемую последовательность seq. Затем для каждого элемента
# из последовательности применяет функцию func и возвращает список результатов. Нужно
# сделать аннотацию кода, что бы запуск mypy --strict проходил без ошибок.
# ruff: noqa

from typing import Callable, Iterable, List, TypeVar

T = TypeVar("T")  # Тип элементов входной последовательности
R = TypeVar("R")  # Тип возвращаемых значений


def process(func: Callable[[T], R], seq: Iterable[T]) -> List[R]:
    """Применяет функцию func к каждому элементу последовательности seq.

    Args:
        func: Функция, преобразующая элемент типа T в тип R
        seq: Итерируемая последовательность элементов типа T

    Returns:
        Список результатов применения func к элементам seq
    """
    return [func(item) for item in seq]


if __name__ == "__main__":
    for indx, (input_items, func, expected_result) in enumerate(
        (
            ((1, 2, 3, 4), lambda x: x**2, [1, 4, 9, 16]),
            (["a", "bb", "ccc"], len, [1, 2, 3]),
            (["a", "bb", "ccc"], str.upper, ["A", "BB", "CCC"]),
        ),
        start=1,
    ):
        received_result = process(func, input_items)
        print(f"кейс {indx} - результат: {received_result}")
        print(f"кейс {indx} - ожидание : {expected_result}")
        assert received_result == expected_result
