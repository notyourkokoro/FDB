import pandas as pd
import pickle
import redis.asyncio as redis

from app.settings import settings


class RedisConnection:
    redis = None

    def connect(self):
        if self.redis is None:
            self.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            self.redis.ping()
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

    async def set_dataframe(self, user_id: str, df: pd.DataFrame):
        await self.redis.set(user_id, pickle.dumps(df))

    async def get_dataframe(self, user_id: str) -> pd.DataFrame:
        return pickle.loads(await self.redis.get(user_id))


memory = RedisConnection()
