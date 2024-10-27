import httpx

from io import BytesIO

from app.settings import settings
from app.exceptions import MirrorHTTPException


class StorageServiceRequests:
    @staticmethod
    async def get_user_file(user_token: str, file_id: int) -> BytesIO:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.storage_url}/storage/download/{file_id}",
                headers={"Authorization": f"Bearer {user_token}"},
            )

        if response.status_code != 200:
            raise MirrorHTTPException(response)
        return BytesIO(response.content)
