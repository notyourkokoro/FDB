from fastapi import FastAPI
from app.auth.schemas import UserRead, UserUpdate
from app.auth.routers import router
from app.auth.manager import fastapi_users


app = FastAPI()

app.include_router(router)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
