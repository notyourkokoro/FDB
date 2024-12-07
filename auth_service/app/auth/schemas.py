import uuid

from pydantic import BaseModel
from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


class UserRead(BaseUser[uuid.UUID]):
    """
    Схема для отображения данных пользователя.
    Использует UUID в качестве идентификатора
    """

    pass


class UserCreate(BaseUserCreate):
    """
    Схема для создания нового пользователя.
    Наследует базовые поля, такие как email и пароль
    """

    pass


class UserUpdate(BaseUserUpdate):
    """
    Схема для обновления данных пользователя.
    Позволяет обновлять определенные поля пользователя
    """

    pass


class JWTToken(BaseModel):
    """
    Схема для JWT-токена.

    Attributes
    ----------
    token : str
        Строковое представление токена
    """

    token: str
