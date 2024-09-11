from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import DBAPIError

from app.models import StorageFile, User
from app.storage import storage
from app.exceptions import (
    FilePermissionException,
    FileNotFoundException,
    UserNotFoundException,
    FileExistsException,
    UserIDException,
)


async def select_user(user_id: str, session: AsyncSession) -> User:
    stmt = select(User).options(selectinload(User.files)).where(User.id == user_id)
    try:
        user = await session.scalar(stmt)
    except DBAPIError:
        raise UserIDException
    if user is None:
        raise UserNotFoundException
    return user


async def select_file(file_id: int, session: AsyncSession) -> StorageFile:
    stmt = (
        select(StorageFile)
        .options(selectinload(StorageFile.users))
        .where(StorageFile.id == file_id)
    )

    storage_file = await session.scalar(stmt)
    if storage_file is None:
        raise FileNotFoundException
    return storage_file


async def create_user_file(
    filename: str, path: str, size: int, user_id: str, session: AsyncSession
) -> StorageFile:

    created_file: StorageFile = StorageFile(
        creator_id=user_id,
        filename=filename,
        path=path,
        size=size,
        type_id=storage.get_filetype_id(filename),
    )

    session.add(created_file)

    user = await select_user(user_id=user_id, session=session)
    user.files.append(created_file)

    await session.commit()

    return created_file


async def select_user_files(
    user_id: str, session: AsyncSession
) -> Sequence[StorageFile]:
    user = await select_user(user_id=user_id, session=session)
    return user.files


async def add_file_to_user(
    user_id: str, to_user_id: str, file_id: int, session: AsyncSession
):
    storage_file = await select_file(file_id=file_id, session=session)

    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    user = await select_user(user_id=to_user_id, session=session)

    if storage_file in user.files:
        raise FileExistsException

    user.files.append(storage_file)
    await session.commit()


async def update_file(
    storage_file: StorageFile, data_to_update: dict, session: AsyncSession
) -> StorageFile:

    stmt = (
        update(StorageFile)
        .where(StorageFile.id == storage_file.id)
        .values(**data_to_update)
    )

    await session.execute(stmt)
    await session.commit()
    await session.refresh(storage_file)

    return storage_file
