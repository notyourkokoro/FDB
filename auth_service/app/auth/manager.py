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
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"Пользователь с ИД {user.id} был успешно зарегистрирован.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f"Пользователь с ИД {user.id} забыл свой пароль. Токен для его восстановления: {token}"
        )

    async def on_after_reset_password(
        self, user: User, request: Optional[Request] = None
    ):
        print(f"Пользователь с ИД {user.id} восстановил свой пароль.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(
            f"Запрошена верификация для пользователя с ИД {user.id}. Токен верификации: {token}"
        )

    async def on_after_update(
        self,
        user: User,
        update_dict: dict[str, Any],
        request: Optional[Request] = None,
    ):
        print(
            f"Пользователь с ИД {user.id} был успешно обновлен со следующими параметрами: {update_dict}."
        )

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        print(f"Пользователь с ИД {user.id} был авторизован.")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        print(f"Пользователь с ИД {user.id} был успешно удален")


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
