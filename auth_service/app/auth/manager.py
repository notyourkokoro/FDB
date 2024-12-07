from typing import Optional, Any
import uuid
from fastapi import Depends, Request, Response

from fastapi_users import BaseUserManager, UUIDIDMixin, FastAPIUsers
from fastapi_users.db import SQLAlchemyUserDatabase

from app.auth.config import auth_backend
from app.auth.models import User
from app.utils import get_user_db
from app.settings import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    Менеджер для управления событиями, связанными с пользователями.
    Использует UUID в качестве идентификаторов пользователей
    """

    # Секретные ключи для токенов сброса пароля и верификации
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Обрабатывает событие после успешной регистрации пользователя

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        request : Optional[Request], optional
            Объект запроса, связанный с регистрацией, если доступен
        """
        print(f"Пользователь с ИД {user.id} был успешно зарегистрирован.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Обрабатывает событие, когда пользователь запрашивает сброс пароля

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        token : str
            Токен для восстановления пароля
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        """
        print(
            f"Пользователь с ИД {user.id} забыл свой пароль. Токен для его восстановления: {token}"
        )

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        """
        Обрабатывает событие после успешного восстановления пароля пользователем

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        """
        print(f"Пользователь с ИД {user.id} восстановил свой пароль.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Обрабатывает событие при прохождении верификации пользоватем

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        token : str
            Токен для верификации
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        """
        print(
            f"Запрошена верификация для пользователя с ИД {user.id}. Токен верификации: {token}"
        )

    async def on_after_update(
        self,
        user: User,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ):
        """
        Обрабатывает событие после обновления информации о пользователе

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        update_dict : dict[str, Any]
            Словарь с обновленными параметрами
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        """
        print(
            f"Пользователь с ИД {user.id} был успешно обновлен со следующими параметрами: {update_dict}."
        )

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        """
        Обрабатывает событие после успешной авторизации пользователя

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        response : Optional[Response], optional
            Объект ответа, связанный с авторизацией, если доступен
        """
        print(f"Пользователь с ИД {user.id} был авторизован.")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        """
        Обрабатывает событие после удаления пользователя

        Parameters
        ----------
        user : User
            Объект ORM-модели пользователя
        request : Optional[Request], optional
            Объект запроса, связанный с этим событием, если доступен
        """
        print(f"Пользователь с ИД {user.id} был успешно удален")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    Возвращает экземпляр UserManager для работы с пользователями

    Parameters
    ----------
    user_db : SQLAlchemyUserDatabase
        Ассинхронное подключение к базе данных

    Yields
    ------
    UserManager
        Экземпляр UserManager для управления событиями пользователей
    """
    yield UserManager(user_db)


# Инициализация FastAPIUsers с указанным менеджером пользователей и бэкендом аутентификации
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Получение текущего активного пользователя
current_user = fastapi_users.current_user(active=True)
