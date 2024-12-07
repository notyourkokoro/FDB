from fastapi import FastAPI

from app.routers import router

# Инициализация FastAPI-приложения
app = FastAPI()
# Добавление маршрутов для работы с файлами
app.include_router(router)
