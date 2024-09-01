from fastapi import FastAPI
from app.schemas import UserRead, UserUpdate
from app.routers import router
from app.manager import fastapi_users


app = FastAPI()

app.include_router(router)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
