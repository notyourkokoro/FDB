import json

from fastapi import status
from fastapi.exceptions import HTTPException


class MirrorHTTPException(HTTPException):
    def __init__(self, response):
        text = json.loads(response.text).get("detail")
        super().__init__(status_code=response.status_code, detail=text)


DataNotFound = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Для начала необходимо загрузить данные!",
)
