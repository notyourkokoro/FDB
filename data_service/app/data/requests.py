import httpx

from io import BytesIO

from app.settings import settings
from app.exceptions import MirrorHTTPException, ServerException
from app.schemas import DataFormat, DataMediaType
from app.utils import TempStorage


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

    @staticmethod
    async def sent_file(
        user_token: str, file_id: int, file_obj: BytesIO, filetype: DataFormat
    ) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                media_type = getattr(DataMediaType, filetype.name).value
                filename = TempStorage.get_name(filetype=filetype)

                response = await client.post(
                    f"{settings.storage_url}/storage/add/version",
                    headers={"Authorization": f"Bearer {user_token}"},
                    params={"based_file_id": file_id},
                    files={
                        "upload_file_obj": (
                            filename,
                            file_obj,
                            media_type,
                        )
                    },
                )
        except Exception:
            raise ServerException

        if response.status_code != 201:
            raise MirrorHTTPException(response)

        return response.json()
