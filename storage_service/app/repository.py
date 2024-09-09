from sqlalchemy.ext.asyncio import AsyncSession

from app.models import StorageFile
from app.storage import storage


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
    await session.commit()

    return created_file
