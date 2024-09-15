from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.data.routers import router
from app.memory import memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    memory.connect()
    yield
    await memory.disconnect()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
