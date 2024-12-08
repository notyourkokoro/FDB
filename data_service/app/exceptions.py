import json
import pandas as pd

from fastapi import status
from fastapi.exceptions import HTTPException


class MirrorHTTPException(HTTPException):
    """
    Исключение для обработки HTTP-ответов с ошибкой,
    возвращаемых другим сервисом
    """

    def __init__(self, response):
        """
        Инициализация исключения

        Parameters
        ----------
        response : Response
            HTTP-ответ, содержащий код состояния и текст ошибки
        """
        # Извлечение текстового описания ошибки из JSON-ответа
        text = json.loads(response.text).get("detail")
        # Инициализация базового класса с кодом состояния и текстом ошибки
        super().__init__(status_code=response.status_code, detail=text)


class ColumnsNotFoundException(HTTPException):
    """
    Исключение для случаев, когда указанные
    колонки отсутствуют в данных
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список названий колонок, которые не найдены в DataFrame
        """
        # Обработка ошибки pandas при отсутствии колонок в DataFrame
        if isinstance(columns[0], pd.errors.UndefinedVariableError):
            error_column = columns[0].args[0].split(" ")[1]
            columns = [error_column[1:-1]]

        # Инициализация базового исключения с текстом об отсутствующих колонках
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колонок с такими именами нет в загруженных данных: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


class ColumnsDuplicateException(HTTPException):
    """
    Исключение для случаев, когда в данных
    обнаружены дублирующиеся колонки
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список названий дублирующихся колонок
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Колонки с такими именами повторяются: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


class NotNumericTypeException(HTTPException):
    """
    Исключение для случаев, когда колонки
    имеют нечисловой тип данных
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        columns : list[str]
            Список названий колонок с некорректным типом данных
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Колонки имеют тип данных, отличный от числового: {columns}".format(
                columns=", ".join(map(str, columns))
            ),
        )


# Исключение для случая, если файл по указанному пути не найден
FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)


# Исключение для ошибок взаимодействия между сервисами
ServerException = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Ошибка при обращении между сервисами!",
)
