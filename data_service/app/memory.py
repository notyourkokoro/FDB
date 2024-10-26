import pandas as pd
import pickle
import redis.asyncio as redis

from app.settings import settings
from app.data.exceptions import DataNotFound


class RedisConnection:
    redis = None

    async def connect(self):
        if self.redis is None:
            self.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            await self.redis.ping()
        except Exception as error:
            print("Неудачная попытка подключиться к Redis: {error}".format(error=error))

    async def disconnect(self):
        if redis is not None:
            try:
                await self.redis.aclose()
            except Exception as error:
                print(
                    "Произошла ошибка при разрыве соединения с Redis: {error}".format(
                        error=error
                    )
                )

    async def set_dataframe(self, user_id: str, df: pd.DataFrame, file_id: int):
        await self.redis.set(f"{user_id}_data", pickle.dumps(df))
        await self.redis.set(f"{user_id}_columns", pickle.dumps(df.columns))
        await self.redis.set(f"{user_id}_file_id", pickle.dumps(file_id))

    async def get_dataframe(self, user_id: str) -> pd.DataFrame:
        data = await self.redis.get(f"{user_id}_data")
        if data is None:
            raise DataNotFound
        return pickle.loads(data)

    async def get_columns(self, user_id: str) -> list:
        columns = await self.redis.get(f"{user_id}_columns")
        if columns is None:
            raise DataNotFound
        return list(pickle.loads(columns))

    async def get_filet_id(self, user_id: str) -> int:
        file_id = await self.redis.get(f"{user_id}_file_id")
        if file_id is None:
            raise DataNotFound
        return pickle.loads(file_id)


memory = RedisConnection()
