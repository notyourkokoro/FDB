import httpx

from app.settings import settings
from app.exceptions import MirrorHTTPException


async def get_user_uuid(user_token: str) -> str:
    """
    Получает UUID пользователя по его токену

    Parameters
    ----------
    user_token : str
        JWT токен пользователя, который будет декодирован для получения UUID

    Returns
    -------
    str
        UUID пользователя, извлеченный из ответа внешнего API

    Raises
    ------
    MirrorHTTPException
        Если ответ от внешнего API не содержит статус 200, тогда пробрасыватся исключение
    """
    # Использование асинхронного клиента для отправки запроса для декодирования токена
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.auth_url}/auth/jwt/decode",  # URL для декодирования токена
            json={"token": user_token},  # Тело запроса с токеном
        )

    # Если ответ от API не содержит статус 200,
    # рейсится исключение, полученное от API
    if response.status_code != 200:
        raise MirrorHTTPException(response)

    # Возвращение UUID пользователя из ответа
    return response.json().get("uuid")
