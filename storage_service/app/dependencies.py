import requests

from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import settings

security = HTTPBearer()


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str | None:
    token = credentials.credentials
    response = requests.post(
        f"{settings.auth_url}/auth/jwt/decode",
        json={"token": token},
    )

    return response.json().get("uuid")
