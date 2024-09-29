from fastapi import status
from fastapi.exceptions import HTTPException

DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)


class ColumnsExistsException(HTTPException):
    def __init__(self, columns: list[str]):
        detail = f"Колонки с такими именами уже существуют: {', '.join(columns)}!"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


EvalException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Некорректное выражение!",
)
