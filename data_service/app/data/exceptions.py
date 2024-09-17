from fastapi import status
from fastapi.exceptions import HTTPException

DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)


class ColumnsNotFound(HTTPException):
    def __init__(self, columns: list[str]):

        detail = f"В загруженных данных найдены столбцы: {', '.join(columns)}!"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
