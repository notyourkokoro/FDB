import httpx

from app.settings import settings
from app.exceptions import MirrorHTTPException


async def get_user_uuid(user_token: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_url}/auth/jwt/decode",
            json={"token": user_token},
        )
    if response.status_code != 200:
        raise MirrorHTTPException(response)
    return response.json().get("uuid")
