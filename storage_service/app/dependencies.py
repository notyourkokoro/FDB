import json
import httpx

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import settings

security = HTTPBearer()


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    token = credentials.credentials
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_url}/auth/jwt/decode",
            json={"token": token},
        )

    if response.status_code != 200:
        text = json.loads(response.text).get("detail")
        raise HTTPException(status_code=response.status_code, detail=text)
    return response.json().get("uuid")
