import json
import pandas as pd

from fastapi import status
from fastapi.exceptions import HTTPException


# Исключение, которое возвращается, если у
# пользователяне установлен DataFrame в Redis
DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)


class MirrorHTTPException(HTTPException):
    """
    Класс исключения для зеркалирования (копирования) исключений с другого API
    """

    def __init__(self, response):
        """
        Инициализация исключения на основе ответа внешнего API

        Parameters
        ----------
        response : Response
            Ответ от внешнего API, который необходимо обработать и зеркалировать
        """
        # Извлечение текста ошибки из ответа внешнего API
        text = json.loads(response.text).get("detail")
        # Инициализация базового исключение с кодом
        # состояния и текстом ошибки из внешнего API
        super().__init__(status_code=response.status_code, detail=text)


class ColumnsNotFoundException(HTTPException):
    """
    Исключение, которое выбрасывается,
    если колонки не были найдены в данных
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения с конкретными колонками, которых нет в данных

        Parameters
        ----------
        columns : list[str]
            Список имен колонок, которых нет в данных
        """
        # Если в списке колонок присутствует ошибка UndefinedVariableError из pandas
        if isinstance(columns[0], pd.errors.UndefinedVariableError):
            # Извлекаем имя несуществующей колонки
            error_column = columns[0].args[0].split(" ")[1]
            columns = [error_column[1:-1]]

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колонок с такими именами нет в загруженных данных: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


class ColumnsDuplicateException(HTTPException):
    """
    Исключение, которое выбрасывается, если в запросе есть дублирующиеся колонки
    """

    def __init__(self, columns: list[str]):
        """
        Инициализация исключения с конкретными колонками, которые повторяются

        Parameters
        ----------
        columns : list[str]
            Список имен колонок, которые встречаются несколько раз
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Колонки с такими именами повторяются: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


# Исключение, которое возвращается,
# если файл не был найден по указанному пути
FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)
