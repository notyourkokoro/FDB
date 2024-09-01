from fastapi import APIRouter

from app.config import auth_backend
from app.manager import fastapi_users
from app.schemas import UserRead, UserCreate

router = APIRouter(tags=["Auth"], prefix="/auth")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
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
