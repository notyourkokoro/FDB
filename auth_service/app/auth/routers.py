import jwt

from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.config import auth_backend
from app.auth.manager import fastapi_users
from app.auth.schemas import JWTToken, UserCreate, UserRead
from app.auth.models import User
from app.database import async_db

# Создание маршрутизатора для работы с авторизацией
router = APIRouter(tags=["auth"], prefix="/auth")

# Добавление маршрутов для аутентификации с использованием JWT
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)


@router.post("/jwt/decode")
async def jwt_decode(
    token: JWTToken, session: AsyncSession = Depends(async_db.get_async_session)
) -> dict:
    """
    Декодирует JWT-токен и возвращает идентификатор пользователя

    Parameters
    ----------
    token : JWTToken
        JWT токен пользователя
    session : AsyncSession
        Асинхронная сессия базы данных, получаемая через Depends

    Returns
    -------
    dict
        Словарь, содержащий идентификатор пользователя (по ключу uuid)

    Raises
    ------
    HTTPException
        Возникает при истечении срока действия токена, неверном токене или отсутствии пользователя
    """
    try:
        user_uuid = jwt.decode(token.token, options={"verify_signature": False}).get(
            "sub"
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный токен.",
        )

    if user_uuid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный токен.",
        )

    # Получение пользователя по идентификатору (если есть такой в БД)
    user = await session.scalar(select(User).where(User.id == user_uuid))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return {"uuid": user_uuid}


# Добавление маршрута для регистрации пользователей
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# Добавление маршрута для верификации пользователей
router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

# Добавление маршрута для сброса пароля
router.include_router(
    fastapi_users.get_reset_password_router(),
)
