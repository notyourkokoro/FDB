import httpx

from app.settings import settings
from app.exceptions import MirrorHTTPException


async def get_user_uuid(user_token: str) -> str:
    """
    Получает UUID пользователя на основе его
    токена через сервис аутентификации

    Parameters
    ----------
    user_token : str
        JWT токен пользователя

    Returns
    -------
    str
        UUID пользователя, извлеченный из
        ответа сервиса аутентификации

    Raises
    ------
    MirrorHTTPException
        Если сервис аутентификации возвращает
        ошибку - пробрасывается исключение
    """
    # Создание асинхронного HTTP-клиента
    async with httpx.AsyncClient() as client:
        # Отправка запроса для декодирования JWT токена
        response = await client.post(
            f"{settings.auth_url}/auth/jwt/decode",
            json={"token": user_token},
        )
    if response.status_code != 200:
        raise MirrorHTTPException(response)
    # Извлечение UUID из ответа и его возвращение
    return response.json().get("uuid")
