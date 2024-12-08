from fastapi import status
from fastapi.exceptions import HTTPException


class BadOperationException(HTTPException):
    """
    Исключение для неправильных операций с данными
    """

    def __init__(self, operations: list[str], value_type: str = "данных"):
        """
        Инициализация исключения

        Parameters
        ----------
        operations : list[str]
            Список допустимых операций
        value_type : str
            Тип данных, к которым применяется операция
            (если тип не указан, то вместо его будет "данных")
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Операция для {value_type} должна быть одной из перечисленных: {operations}".format(
                value_type=value_type, operations=", ".join(map(str, operations))
            ),
        )


class EmptyColumnException(HTTPException):
    """
    Исключение для случая, когда
    столбец состоит из None
    """

    def __init__(self, column: str):
        """
        Инициализация исключения

        Parameters
        ----------
        column : str
            Название столбца, который оказался пустым
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В одном из переданных столбцов нет данных: {column}".format(
                column=column
            ),
        )


class NanColumnsException(HTTPException):
    """
    Исключение для случая, когда в
    колонках есть значения NaN
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список столбцов, содержащих NaN значения
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Следующие колонки содерджат пустые значения: {columns}".format(
                columns=", ".join(columns)
            ),
        )


class BinaryColumnsException(HTTPException):
    """
    Исключение для случаев, когда столбцы
    содержат значения, отличные от 0, 1 и None
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список столбцов, содержащих
            некорректные значения
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Следующие колонки имеют значения, отличные от 0, 1 и None: {columns}".format(
                columns=", ".join(columns)
            ),
        )


BASE_PRINT = "При выполнении функции {name} с данными {data} возникла ошибка: {error}"


# Исключение для неправильных параметров для определения групп
BadGroupParamsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неверные параметры для создания групп!",
)
