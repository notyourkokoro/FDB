import os
from typing import Sequence

from fastapi import APIRouter, UploadFile, File, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.storage import storage
from app.schemas import AddUserFile, StorageFileRead
from app.repository import create_user_file, select_user_files, add_file_to_user
from app.dependencies import get_current_user_uuid
from app.exceptions import FileFormatException, FileNameException

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post(
    "/upload", status_code=status.HTTP_201_CREATED, response_model=StorageFileRead
)
async def upload_file(
    file_obj: UploadFile = File(...),
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileRead:
    filepath = storage.get_filepath(filename=file_obj.filename, user_id=user_id)

    if not file_obj.filename.endswith(("xlsx", "xls", "csv")):
        raise FileFormatException

    if os.path.exists(filepath):
        raise FileNameException

    with open(filepath, "wb") as output_file:
        output_file.write(file_obj.file.read())

    created_file = await create_user_file(
        filename=file_obj.filename,
        path=filepath,
        size=file_obj.size,
        user_id=user_id,
        session=session,
    )

    return created_file


@router.get("/list", response_model=list[StorageFileRead])
async def get_user_files(
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> Sequence[StorageFileRead]:
    return await select_user_files(user_id=user_id, session=session)


@router.post("/add_user", status_code=status.HTTP_201_CREATED)
async def add_filelink_to_user(
    data_to_add: AddUserFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    await add_file_to_user(
        user_id=user_id,
        to_user_id=data_to_add.to_user_id,
        file_id=data_to_add.file_id,
        session=session,
    )
