from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import router
from app.memory import RedisConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления подключением к Redis
    при старте и завершении работы приложения

    Parameters
    ----------
    app : FastAPI
        Экземпляр приложения FastAPI
    """
    # Подключаемся к Redis перед запуском приложения
    await RedisConnection.connect()
    yield  # Приложение будет работать между yield
    # Отключаемся от Redis при завершении работы приложения
    await RedisConnection.disconnect()


# Инициализация FastAPI приложения с использованием
# контекстного менеджера для Redis
app = FastAPI(lifespan=lifespan)

# Добавление маршрутов в приложение
app.include_router(router)
