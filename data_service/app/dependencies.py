import pandas as pd

from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.requests import get_user_uuid
from app.memory import RedisConnection


# Объект для извлечения токена из заголовков HTTP
security = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Извлечение токена текущего пользователя из HTTP-заголовка

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий токен авторизации

    Returns
    -------
    str
        Токен текущего пользователя
    """
    return credentials.credentials


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Получение UUID текущего пользователя на основе его токена

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий токен авторизации

    Returns
    -------
    str
        UUID текущего пользователя
    """
    # Извлечение токена из данных заголовка
    token = credentials.credentials
    # Получение UUID пользователя, используя JWT-токен
    return await get_user_uuid(user_token=token)


async def get_user_data(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> pd.DataFrame:
    """
    Извлечение данных пользователя из хранилища Redis

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий токен авторизации

    Returns
    -------
    dict
        Словарь, содержащий:
        - user_id: UUID пользователя
        - data: Табличные данные пользователя в формате pandas DataFrame
        - file_id: Идентификатор файла, связанного с данными
    """
    # Получение UUID текущего пользователя
    user_id = await get_current_user_uuid(credentials=credentials)
    # Извлечение данных пользователя из Redis
    df = await RedisConnection.get_dataframe(user_id=user_id)
    # Получение идентификатора файла, связанного с pandas DataFrame
    file_id = await RedisConnection.get_filet_id(user_id=user_id)
    return {"user_id": user_id, "data": df, "file_id": file_id}
