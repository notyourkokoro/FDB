from uuid import UUID

from sqlalchemy import select, and_
from app.models import UserGroup, UserFile, GroupFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository import (
    select_file,
    select_user,
)


class StorageFilePermission:
    """
    Класс для проверки прав доступа пользователей к файлам в хранилище
    """

    @staticmethod
    async def has_user_access_to_file(
        user_id: UUID, file_id: int, session: AsyncSession
    ) -> bool:
        """
        Проверяет, имеет ли пользователь доступ к файлу,
        либо через его личные файлы,
        либо через группы, к которым он принадлежит

        Parameters
        ----------
        user_id : UUID
            Идентификатор пользователя
        file_id : int
            Идентификатор файла
        session : AsyncSession
            Асинхронная сессия базы данных

        Returns
        ----------
        bool
            True, если у пользователя есть доступ к файлу, иначе False
        """

        # Подзапрос для получения всех групп пользователя
        user_groups_subquery = (
            select(UserGroup.group_id).where(UserGroup.user_id == user_id).subquery()
        )

        # Проверка наличия файла в личных файлах пользователя (UserFile)
        user_files_query = select(UserFile).where(
            and_(UserFile.user_id == user_id, UserFile.file_id == file_id)
        )
        user_file_exists = await session.execute(user_files_query)
        user_file_exists = user_file_exists.scalar() is not None

        # Проверка наличия файла в группах, к которым принадлежит пользователь (GroupFile)
        group_files_query = select(GroupFile).where(
            and_(
                GroupFile.file_id == file_id,
                GroupFile.group_id.in_(user_groups_subquery),
            )
        )
        group_file_exists = await session.execute(group_files_query)
        group_file_exists = group_file_exists.scalar() is not None

        # Если файл найден либо в личных файлах пользователя, либо в группах, возвращаем True
        return user_file_exists or group_file_exists

    @staticmethod
    async def check_user_access_with_data(
        user_id: str, file_id: int, session: AsyncSession
    ) -> dict:
        """
        Проверяет, имеет ли пользователь доступ к файлу и
        возвращает данные о пользователе и файле, если доступ есть

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя в виде строки
        file_id : int
            Идентификатор файла
        session : AsyncSession
            Асинхронная сессия базы данных

        Returns
        ----------
        dict
            Словарь с информацией о доступе, пользователе и файле.
            Пример:
            {"access": True, "user": user_data, "storage_file": file_data}
            или {"access": False} в случае отказа в доступе
        """
        # Проверка на то, имеет ли пользователь доступ к файлу
        if (
            await StorageFilePermission.has_user_access_to_file(
                user_id=UUID(user_id), file_id=file_id, session=session
            )
            is False
        ):
            return {"access": False}

        # Получаем данные о пользователе и файле
        user = await select_user(user_id=user_id, session=session)
        storage_file = await select_file(file_id=file_id, session=session)

        # Возвращаем информацию о доступе, пользователе и файле
        return {"user": user, "storage_file": storage_file, "access": True}
