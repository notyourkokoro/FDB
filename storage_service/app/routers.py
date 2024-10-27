from typing import Sequence

from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.storage import storage
from app.schemas import (
    AddUserFile,
    StorageFileRead,
    StorageFileList,
    StorageFilePatch,
    AddUsersFile,
    StorageFileReadFull,
)
from app.repository import (
    create_user_file,
    remove_file,
    select_user_files,
    add_file_to_user,
    update_file,
    add_file_to_users,
)
from app.dependencies import get_current_user_uuid
from app.exceptions import (
    FileFormatException,
    FilePermissionException,
    BasedOnException,
)
from app.permissions import StorageFilePermission
from app.models import FileTypeEnum

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    upload_file_obj: UploadFile = File(...),
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileRead:
    filepath = storage.get_filepath(filename=upload_file_obj.filename, user_id=user_id)

    if not upload_file_obj.filename.endswith(("xlsx", "xls", "csv")):
        raise FileFormatException

    storage.create_file(filepath, upload_file_obj.file)

    created_file = await create_user_file(
        filename=upload_file_obj.filename,
        path=filepath,
        size=upload_file_obj.size,
        user_id=user_id,
        session=session,
    )

    return created_file


@router.post(
    "/based/{file_id}",
    status_code=status.HTTP_201_CREATED,
)
async def based_on(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileReadFull:
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException

    storage_file = data["storage_file"]

    if str(storage_file.creator_id) == user_id:
        raise BasedOnException

    filepath = storage.get_filepath(filename=storage_file.filename, user_id=user_id)

    storage.create_based_on(filepath_read=storage_file.path, filepath_output=filepath)
    created_file = await create_user_file(
        filename=storage_file.filename,
        path=filepath,
        size=storage_file.size,
        user_id=user_id,
        based_on_id=file_id,
        session=session,
    )

    return created_file


@router.post(
    "/add_user",
    status_code=status.HTTP_201_CREATED,
)
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


@router.post("/add_users", status_code=status.HTTP_201_CREATED)
async def add_filelink_to_users(
    data_to_add: AddUsersFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    await add_file_to_users(
        user_id=user_id,
        to_user_ids=data_to_add.to_user_ids,
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
) -> StorageFileReadFull:
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
) -> StorageFileReadFull:
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


@router.delete("/delete/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException
    storage_file = data["storage_file"]

    storage.delete_file(storage_file.path)
    await remove_file(storage_file=storage_file, session=session)
