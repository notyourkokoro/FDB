from uuid import UUID

from sqlalchemy import select, and_
from app.models import UserGroup, UserFile, GroupFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import (
    select_file,
    select_user,
)


class StorageFilePermission:
    @staticmethod
    async def has_user_access_to_file(
        user_id: UUID, file_id: int, session: AsyncSession
    ) -> bool:
        # Подзапрос для получения групп пользователя
        user_groups_subquery = (
            select(UserGroup.group_id).where(UserGroup.user_id == user_id).subquery()
        )

        # Проверка на наличие файла в личных файлах пользователя (User.files)
        user_files_query = select(UserFile).where(
            and_(UserFile.user_id == user_id, UserFile.file_id == file_id)
        )
        user_file_exists = await session.execute(user_files_query)
        user_file_exists = user_file_exists.scalar() is not None

        # Проверка на наличие файла в группах пользователя
        group_files_query = select(GroupFile).where(
            and_(
                GroupFile.file_id == file_id,
                GroupFile.group_id.in_(user_groups_subquery),
            )
        )
        group_file_exists = await session.execute(group_files_query)
        group_file_exists = group_file_exists.scalar() is not None

        # Если файл есть в личных файлах или в группах, возвращаем True
        return user_file_exists or group_file_exists

    @staticmethod
    async def check_user_access_with_data(
        user_id: str, file_id: int, session: AsyncSession
    ) -> dict:
        if (
            await StorageFilePermission.has_user_access_to_file(
                user_id=UUID(user_id), file_id=file_id, session=session
            )
            is False
        ):
            return {"access": False}

        user = await select_user(user_id=user_id, session=session)
        storage_file = await select_file(file_id=file_id, session=session)
        return {"user": user, "storage_file": storage_file, "access": True}
