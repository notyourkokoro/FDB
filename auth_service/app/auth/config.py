from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from app.settings import settings

# Инициализация Bearer-транспортировки с указанием URL для получения токена
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    """
    Получение стратегии аутентификации (JWT)

    Returns
    -------
    JWTStrategy
        Объект стратегии JWT, настроенный с секретным ключом,
        временем жизни токена и алгоритмом шифрования
    """
    return JWTStrategy(
        secret=settings.secret_key,
        lifetime_seconds=3600,
        algorithm=settings.secret_algorithm,
    )


# Инициализация бэкенда для аутентификации
# (транспорт Bearer и стратегия JWT)
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
