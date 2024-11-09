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

router = APIRouter(tags=["auth"], prefix="/auth")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)


@router.post("/jwt/decode")
async def jwt_decode(
    token: JWTToken, session: AsyncSession = Depends(async_db.get_async_session)
):
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

    user = await session.scalar(select(User).where(User.id == user_uuid))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден.",
        )

    return {"uuid": user_uuid}


router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

router.include_router(
    fastapi_users.get_reset_password_router(),
)
