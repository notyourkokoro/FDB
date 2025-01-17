from fastapi import FastAPI
from app.auth.schemas import UserRead, UserUpdate
from app.auth.routers import router as auth_router
from app.auth.manager import fastapi_users
from app.group.routers import router as group_router

from app.auth.models import User  # noqa F401 - так надо
from app.group.models import Group  # noqa F401 - так надо


# Инициализация FastAPI-приложения
app = FastAPI()

# Добавление маршрутов для работы с авторизацией
app.include_router(auth_router)
# Добавление маршрутов для работы с пользователями
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
# Добавление маршрутов для работы с пользовательскими группами
app.include_router(group_router)
