from fastapi import status
from fastapi.exceptions import HTTPException


class UsersNotFoundException(HTTPException):
    """
    Исключение, выбрасываемое при отсутствии пользователей с заданными идентификаторами

    Parameters
    ----------
    user_ids : list[str]
        Список идентификаторов пользователей, которые не найдены
    """

    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователи с такими ИД не найдены: {ids}!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


class UsersInGroupExistsException(HTTPException):
    """
    Исключение, выбрасываемое при попытке добавить пользователей,
    уже имеющих доступ к группе

    Parameters
    ----------
    user_ids : list[str]
        Список идентификаторов пользователей, которые уже состоят в группе
    """

    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="К данной группе у пользователей: {ids} - уже есть доступ!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


# Исключение для случая, когда группа с таким именем уже существует
GroupExistsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Группа с таким именем уже существует!",
)


# Исключение для случая, когда пользователь с указанным идентификатором не найден
UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с таким ИД не найден!",
)


# Исключение для случая, когда группа с указанным идентификатором не найдена
GroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Группа c таким ИД не найдена!",
)


# Исключение для случаев, когда операция с группой запрещена
GroupPermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с группой может производить только ее участник!",
)


# Исключение для случая, когда пользователь пытается удалить себя из группы
DeleteUserFromGroupException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь не может самоустраниться из группы!",
)


# Исключение для случаев, когда пользователь не состоит в группе,
# но пытается как-либо с ней взаимодействовать
ContaionsUserInGroupException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь с таким ИД не состоит в группе!",
)
