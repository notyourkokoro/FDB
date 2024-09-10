import os
from typing import Sequence

from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.storage import storage
from app.schemas import AddUserFile, StorageFileRead, StorageFileList
from app.repository import (
    create_user_file,
    select_user_files,
    add_file_to_user,
    select_file,
    select_user,
)
from app.dependencies import get_current_user_uuid
from app.exceptions import (
    FileFormatException,
    FileNameException,
    FilePermissionException,
)
from app.permissions import StorageFilePermission

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
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


@router.get("/list")
async def get_user_files(
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> Sequence[StorageFileList]:
    return await select_user_files(user_id=user_id, session=session)


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileRead:
    storage_file = await select_file(file_id=file_id, session=session)
    user = await select_user(user_id=user_id, session=session)

    if (
        StorageFilePermission.check_user_access(user=user, storage_file=storage_file)
        is False
    ):
        raise FilePermissionException
    return storage_file


@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> FileResponse:
    storage_file = await get_file(file_id=file_id, user_id=user_id, session=session)
    return FileResponse(storage_file.path, filename=storage_file.filename)
