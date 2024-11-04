import pandas as pd

from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.requests import get_user_uuid
from app.memory import RedisConnection


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


async def get_user_data(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> pd.DataFrame:
    user_id = await get_current_user_uuid(credentials=credentials)
    df = await RedisConnection.get_dataframe(user_id=user_id)
    file_id = await RedisConnection.get_filet_id(user_id=user_id)
    return {"user_id": user_id, "data": df, "file_id": file_id}
