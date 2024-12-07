import json
import httpx

from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.settings import settings

# Объект для извлечения токена из заголовков HTTP
security = HTTPBearer()


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Функция для получения UUID текущего пользователя с использованием JWT-токена

    Parameters
    ----------
    credentials : HTTPAuthorizationCredentials
        Данные, содержащие JWT-токен, извлекаемые из заголовков запроса

    Returns
    -------
    str
        UUID текущего пользователя, декодированный из токена

    Raises
    ------
    HTTPException
        Если токен недействителен, истек или сервис проверки токена возвращает ошибку
    """
    # Извлечение токена
    token = credentials.credentials

    # Создаем HTTP-клиент для отправки запроса в `auth-service` для проверки токена
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_url}/auth/jwt/decode",
            json={"token": token},
        )

    # Если статус ответа не успешен, рейсится исключение с деталями ошибки
    if response.status_code != 200:
        text = json.loads(response.text).get("detail")
        raise HTTPException(status_code=response.status_code, detail=text)

    # Возвращаем UUID пользователя из ответа сервиса
    return response.json().get("uuid")
