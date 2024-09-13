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

FilePermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с файлом может производить только его владелец!",
)


FileNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл c таким ИД не найден!",
)

FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)


UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с таким ИД не найден!",
)


class UsersNotFoundException(HTTPException):
    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователи с такими ИД не найдены: {ids}!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


class FileExistsException(HTTPException):
    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="К данному файлу у пользователей: {ids} - уже есть доступ!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )
