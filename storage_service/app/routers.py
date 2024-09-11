from typing import Sequence

from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.storage import storage
from app.schemas import AddUserFile, StorageFileRead, StorageFileList, StorageFilePatch
from app.repository import (
    create_user_file,
    select_user_files,
    add_file_to_user,
    update_file,
)
from app.dependencies import get_current_user_uuid
from app.exceptions import (
    FileFormatException,
    FilePermissionException,
)
from app.permissions import StorageFilePermission
from app.models import FileTypeEnum

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
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException
    return data["storage_file"]


@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> FileResponse:
    storage_file = await get_file(file_id=file_id, user_id=user_id, session=session)
    return FileResponse(storage_file.path, filename=storage_file.filename)


@router.patch("/rename/{file_id}")
async def patch_file(
    file_id: int,
    data_to_patch: StorageFilePatch,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileRead:
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException

    storage_file = data["storage_file"]
    filetype = FileTypeEnum(storage_file.type_id).name
    filepath = storage.get_filepath(
        filename="{name}.{type}".format(name=data_to_patch.filename, type=filetype),
        user_id=user_id,
    )

    storage.rename_file(current_path=storage_file.path, new_path=filepath)

    await update_file(
        storage_file=storage_file,
        data_to_update={"filename": data_to_patch.filename, "path": filepath},
        session=session,
    )

    return storage_file
