from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.requests import get_user_uuid


security = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    return credentials.credentials


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    token = credentials.credentials
    return await get_user_uuid(user_token=token)
