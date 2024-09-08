import jwt

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from app.config import auth_backend
from app.manager import fastapi_users
from app.schemas import UserRead, UserCreate, JWTToken

router = APIRouter(tags=["auth"], prefix="/auth")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)


@router.post("/jwt/decode")
async def jwt_decode(token: JWTToken):
    try:
        return jwt.decode(token.token, options={"verify_signature": False}).get("sub")
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


router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

router.include_router(
    fastapi_users.get_reset_password_router(),
)
