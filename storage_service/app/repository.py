from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Group, StorageFile, User
from app.storage import StogareController
from app.exceptions import (
    FileGroupExistsException,
    FilePermissionException,
    FileNotFoundException,
    UserNotFoundException,
    FileExistsException,
    UsersNotFoundException,
    UserAccessToStorageFile,
    GroupNotFoundException,
    GroupPermissionException,
    FileInGroupNotFoundException,
)


async def select_user(user_id: str, session: AsyncSession) -> User:
    stmt = select(User).options(selectinload(User.files)).where(User.id == user_id)
    user = await session.scalar(stmt)
    if user is None:
        raise UserNotFoundException
    return user


async def select_users(session: AsyncSession, user_ids: list[str]) -> list[User]:
    stmt = select(User).where(User.id.in_(user_ids))
    users = list(await session.scalars(stmt))

    if len(user_ids) != len(users):
        current_user_ids = [user.id for user in users]
        raise UsersNotFoundException(
            user_ids=list(filter(lambda x: x not in current_user_ids, user_ids))
        )

    return users


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


async def select_group(group_id: int, session: AsyncSession) -> Group:
    stmt = (
        select(Group)
        .options(selectinload(Group.users))
        .options(selectinload(Group.files))
        .where(Group.id == group_id)
    )

    group = await session.scalar(stmt)
    if group is None:
        raise GroupNotFoundException
    return group


async def create_user_file(
    filename: str,
    path: str,
    size: int,
    user_id: str,
    session: AsyncSession,
    version: int = 1,
    based_on_id: int | None = None,
) -> StorageFile:

    created_file: StorageFile = StorageFile(
        creator_id=user_id,
        filename=filename,
        path=path,
        size=size,
        type_id=StogareController.get_filetype_id(filename),
        version=version,
        based_on_id=based_on_id,
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
        raise FileExistsException([to_user_id])

    user.files.append(storage_file)
    await session.commit()


async def add_file_to_users(
    user_id: str, to_user_ids: list[str], file_id: int, session: AsyncSession
):
    storage_file = await select_file(file_id=file_id, session=session)

    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    users = await select_users(session=session, user_ids=to_user_ids)

    users_with_file = []
    for user in users:
        if user in storage_file.users:
            users_with_file.append(user.id)

    if len(users_with_file) != 0:
        raise FileExistsException(users_with_file)

    storage_file.users.extend(list(users))
    await session.commit()


async def update_file(
    storage_file: StorageFile, data_to_update: dict, session: AsyncSession
) -> StorageFile:

    stmt = (
        update(StorageFile)
        .where(
            (StorageFile.creator_id == storage_file.creator_id)
            & (StorageFile.filename == storage_file.filename)
        )
        .values(**data_to_update)
    )

    await session.execute(stmt)
    await session.commit()
    await session.refresh(storage_file)

    return storage_file


async def remove_file(storage_file: StorageFile, session: AsyncSession):
    await session.delete(storage_file)
    await session.commit()


async def remove_user_from_file(
    storage_file: StorageFile, user_id: str, session: AsyncSession
):
    user = await select_user(user_id=user_id, session=session)
    if user not in storage_file.users:
        raise UserAccessToStorageFile

    storage_file.users.remove(user)
    await session.commit()


async def add_file_for_group(
    user_id: str, group_id: str, file_id: int, session: AsyncSession
):
    storage_file = await select_file(file_id=file_id, session=session)

    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    group = await select_group(group_id=group_id, session=session)

    if user_id not in [str(user.id) for user in group.users]:
        raise GroupPermissionException

    if storage_file in group.files:
        raise FileGroupExistsException(name=group.name)

    group.files.append(storage_file)
    await session.commit()


async def remove_file_from_group(group: Group, file_id: int, session: AsyncSession):
    storage_file = await select_file(file_id=file_id, session=session)
    if storage_file not in group.files:
        raise FileInGroupNotFoundException

    group.files.remove(storage_file)
    await session.commit()
