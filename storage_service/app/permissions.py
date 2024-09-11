from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, StorageFile
from app.repository import (
    select_file,
    select_user,
)


class StorageFilePermission:
    @staticmethod
    def check_user_access(user: User, storage_file: StorageFile) -> bool:
        if user.is_superuser:
            return True
        if user.id == storage_file.creator_id:
            return True
        if storage_file in user.files:
            return True
        return False

    @staticmethod
    async def check_user_access_with_data(
        user_id: str, storage_file_id: int, session: AsyncSession
    ) -> dict:
        user = await select_user(user_id=user_id, session=session)
        storage_file = await select_file(file_id=storage_file_id, session=session)

        if (
            StorageFilePermission.check_user_access(
                user=user, storage_file=storage_file
            )
            is False
        ):
            return {"access": False}

        return {"user": user, "storage_file": storage_file, "access": True}
