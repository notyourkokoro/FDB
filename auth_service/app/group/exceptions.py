from fastapi import status
from fastapi.exceptions import HTTPException


class UsersNotFoundException(HTTPException):
    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователи с такими ИД не найдены: {ids}!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


class UsersInGroupExistsException(HTTPException):
    def __init__(self, user_ids: list[str]):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="К данной группе у пользователей: {ids} - уже есть доступ!".format(
                ids=", ".join(map(str, user_ids))
            ),
        )


GroupExistsException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Группа с таким именем уже существует!",
)


UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Пользователь с таким ИД не найден!",
)


GroupNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Группа c таким ИД не найдена!",
)


GroupPermissionException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Любую операцию с группой может производить только ее участник!",
)

DeleteUserFromGroupException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь не может самоустраниться из группы!",
)

ContaionsUserInGroupException = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Пользователь с таким ИД не состоит в группе!",
)
