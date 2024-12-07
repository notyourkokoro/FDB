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
    Получение токена авторизации текущего пользователя

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий информацию о токене из заголовков HTTP-запроса

    Returns
    -------
    str
        Токен авторизации текущего пользователя
    """
    return credentials.credentials


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Получение уникального идентификатора пользователя на основе токена

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий информацию о токене из заголовков HTTP-запроса

    Returns
    -------
    str
        UUID пользователя, полученный на основе переданного токена
    """
    # Извлечение токена из учетных данных и находие UUID пользователя
    token = credentials.credentials
    return await get_user_uuid(user_token=token)


async def get_user_data(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> pd.DataFrame:
    """
    Получение данных о загруженном pandas DataFrame пользователем из
    Redis на основе его уникального идентификатора

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Объект, содержащий информацию о токене из заголовков HTTP-запроса

    Returns
    -------
    dict
        Словарь с данными пользователя, включая его идентификатор и DataFrame с данными
    """
    # Получаем UUID пользователя по токену и извлекаем DataFrame из Redis
    user_id = await get_current_user_uuid(credentials=credentials)
    df = await RedisConnection.get_dataframe(user_id=user_id)

    # Возвращаем данные в виде словаря с идентификатором пользователя и DataFrame
    return {"user_id": user_id, "data": df}
