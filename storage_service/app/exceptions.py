from fastapi import status
from fastapi.exceptions import HTTPException

FileFormatException = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    detail="Данный формат файла не поддерживается.",
)

FileNameException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Файл с таким именем уже существует!",
)
