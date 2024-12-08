from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.data.routers import router as data_router
from app.statistic.routers import router as statistic_router
from app.calculation.routers import router as calculation_router
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

# Добавление маршрутов для работы с данными
app.include_router(data_router)
# Добавление маршрутов для работы со статистикой
app.include_router(statistic_router)
# Добавление маршрутов для работы с калькуляторами
app.include_router(calculation_router)
