import json

from fastapi import status
from fastapi.exceptions import HTTPException


class MirrorHTTPException(HTTPException):
    def __init__(self, response):
        text = json.loads(response.text).get("detail")
        super().__init__(status_code=response.status_code, detail=text)


class ColumnsNotFoundException(HTTPException):
    def __init__(self, columns: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Колонок с такими именами нет в загруженных данных: {columns}!".format(
                columns=", ".join(map(str, columns))
            ),
        )


FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)
