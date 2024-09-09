from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import StorageFile, User
from app.storage import storage


async def select_user(user_id: str, session: AsyncSession) -> User:
    stmt = select(User).options(selectinload(User.files)).where(User.id == user_id)
    return await session.scalar(stmt)


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
