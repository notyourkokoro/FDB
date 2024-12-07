from fastapi import status
from fastapi.exceptions import HTTPException

# Исключение для случая, когда формат файла не поддерживается
FileFormatException = HTTPException(
    status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
    detail="Данный формат файла не поддерживается.",
)


# Исключение для случая, когда при загрузке оказывается так,
# что файл с таким именем уже существует
FileNameException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Файл с таким именем уже существует!",
)


# Исключение для случая, когда пользователь пытается изменить файл,
# но не является его владельцем
FilePermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с файлом может производить только его владелец!",
)


# Исключение для случая, когда файл с указанным ИД не найден
FileNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл c таким ИД не найден!",
)


# Исключение для случая, когда файл не найден по указанному пути
FilepathNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл по данному пути не найден!",
)


# Исключение для случая, когда пользователь с таким ИД не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с таким ИД не найден!",
)


# Исключение для случая, когда пользователь не имеет доступа к файлу,
# к которому пытается обратиться
UserAccessToStorageFile = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Пользователь не имеет доступа к данному файлу!",
)


# Исключение для случая, когда пользователь не может удалить связь между своим файлом и собой
DeleteUserFileException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь не может удалить связь между своим файлом и собой!",
)


# Исключение для случая, когда группа с таким ИД не найдена
GroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Группа c таким ИД не найдена!",
)


# Исключение для случая, когда пользователь пытается выполнить операцию с группой, к которой он не относится
GroupPermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с группой может производить только ее участник!",
)


# Исключение для случая, когда пользователь пытается создать файл на основе файла, который он загрузил
BasedOnException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Нельзя создать файл на основе самого себя, будучи его создателем!",
)


# Исключение для случая, когда файл не найден в группе по ИД
FileInGroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Файл в группе c таким ИД не найден!",
)


class UsersNotFoundException(HTTPException):
    """
    Исключение для случая, когда не удается
    найти пользователей по переданным ИД
    """

    def __init__(self, user_ids: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        user_ids : list[str]
            Список ИД пользователей, которых не удалось найти
        """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователи с такими ИД не найдены: {ids}!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


class FileExistsException(HTTPException):
    """
    Исключение для случая, когда доступ к файлу
    уже предоставлен указанным пользователям
    """

    def __init__(self, user_ids: list[str]):
        """
        Инициализация исключения

        Parameters
        ----------
        user_ids : list[str]
            Список ИД пользователей, которые уже имеют доступ к файлу
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="К данному файлу у пользователей: {ids} - уже есть доступ!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


class FileGroupExistsException(HTTPException):
    """
    Исключение для случая, когда к
    пользовательскойгруппе уже привязан файлу
    """

    def __init__(self, name: str):
        """
        Инициализация исключения

        Parameters
        ----------
        name : str
            Имя группы, которой уже предоставлен доступ к файлу.
        """
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='К данному файлу у группы: "{name}" - уже есть доступ!'.format(
                name=name
            ),
        ),
