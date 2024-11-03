import pandas as pd
import pickle
import redis.asyncio as redis

from app.settings import settings
from app.exceptions import DataNotFound


class RedisConnection:
    redis = None

    @classmethod
    async def connect(cls):
        if cls.redis is None:
            cls.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            await cls.redis.ping()
        except Exception as error:
            print("Неудачная попытка подключиться к Redis: {error}".format(error=error))

    @classmethod
    async def disconnect(cls):
        if redis is not None:
            try:
                await cls.redis.aclose()
            except Exception as error:
                print(
                    "Произошла ошибка при разрыве соединения с Redis: {error}".format(
                        error=error
                    )
                )

    @classmethod
    async def get_dataframe(cls, user_id: str) -> pd.DataFrame:
        data = await cls.redis.get(f"{user_id}_data")
        if data is None:
            raise DataNotFound
        return pickle.loads(data)
