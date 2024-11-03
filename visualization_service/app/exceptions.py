import json
import pandas as pd

from fastapi import status
from fastapi.exceptions import HTTPException


DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)


class MirrorHTTPException(HTTPException):
    def __init__(self, response):
        text = json.loads(response.text).get("detail")
        super().__init__(status_code=response.status_code, detail=text)


class ColumnsNotFoundException(HTTPException):
    def __init__(self, columns: list[str]):
        if isinstance(columns[0], pd.errors.UndefinedVariableError):
            error_column = columns[0].args[0].split(" ")[1]
            columns = [error_column[1:-1]]

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колонок с такими именами нет в загруженных данных: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


class ColumnsDuplicateException(HTTPException):
    def __init__(self, columns: list[str]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Колонки с такими именами повторяются: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)
