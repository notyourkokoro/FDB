from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import router
from app.memory import RedisConnection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await RedisConnection.connect()
    yield
    await RedisConnection.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
