from fastapi import FastAPI, Depends

from app.settings import settings
from app.storage import storage
from app.routers import router
from app.dependencies import get_current_user_uuid

app = FastAPI()
app.include_router(router)


@app.get("/storage_path")
def get_storage():
    return settings.storage_path


@app.get("/filetype_id")
def get_filetype(filename: str):
    return storage.get_filetype_id(filename)


@app.get("/current_user")
def get_current_user(user_id: str = Depends(get_current_user_uuid)):
    return user_id
