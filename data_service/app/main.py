from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.data.routers import router as data_router
from app.statistic.routers import router as statistic_router
from app.memory import memory


@asynccontextmanager
async def lifespan(app: FastAPI):
    await memory.connect()
    yield
    await memory.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(data_router)
app.include_router(statistic_router)
