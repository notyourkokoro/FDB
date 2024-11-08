from fastapi import status
from fastapi.exceptions import HTTPException


class BadOperationException(HTTPException):
    def __init__(self, operations: list[str], value_type: str = "данных"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Операция для {value_type} должна быть одной из перечисленных: {operations}".format(
                value_type=value_type, operations=", ".join(map(str, operations))
            ),
        )


class EmptyColumnException(HTTPException):
    def __init__(self, column: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="В одном из переданных столбцов нет данных: {column}".format(
                column=column
            ),
        )


class NanColumnsException(HTTPException):
    def __init__(self, columns: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Следующие колонки содердят пустые значения: {columns}".format(
                columns=", ".join(columns)
            ),
        )


class BinaryColumnsException(HTTPException):
    def __init__(self, columns: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Следующие колонки имеют значения, отличные от 0, 1 и None: {columns}".format(
                columns=", ".join(columns)
            ),
        )


BASE_PRINT = "При выполнении функции {name} с данными {data} возникла ошибка: {error}"


BadGroupParamsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Неверные параметры для создания групп!",
)
