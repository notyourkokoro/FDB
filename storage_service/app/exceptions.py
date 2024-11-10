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

UserAccessToStorageFile = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Пользователь не имеет доступа к данному файлу!",
)

DeleteUserFileException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь не может удалить связь между своим файлом и собой!",
)

GroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Группа c таким ИД не найдена!",
)


GroupPermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с группой может производить только ее участник!",
)

BasedOnException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Нельзя создать файл на основе самого себя, будучи его создателем!",
)


FileInGroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл в группе c таким ИД не найден!",
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


class FileGroupExistsException(HTTPException):
    def __init__(self, name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='К данному файлу у группы: "{name}" - уже есть доступ!'.format(
                name=name
            ),
        ),
