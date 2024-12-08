import pandas as pd
import pickle
import redis.asyncio as redis

from app.settings import settings
from app.data.exceptions import DataNotFound


class RedisConnection:
    """
    Класс для управления подключением и взаимодействием с Redis

    Attributes
    ----------
    redis : redis.Redis
        Экземпляр подключения к Redis
    """

    redis = None

    @classmethod
    async def connect(cls):
        """
        Устанавливает соединение с Redis, если оно еще не установлено

        Raises
        ------
        Exception
            Если не удается подключиться к Redis - ошибка
        """
        if cls.redis is None:
            cls.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            # Проверка доступности подключения
            await cls.redis.ping()
        except Exception as error:
            print("Неудачная попытка подключиться к Redis: {error}".format(error=error))

    @classmethod
    async def disconnect(cls):
        """
        Закрывает соединение с Redis

        Raises
        ------
        Exception
            Если происходит ошибка при разрыве соединения
        """
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
    async def set_dataframe(
        cls, user_id: str, df: pd.DataFrame, file_id: int | None = None
    ):
        """
        Сохраняет DataFrame и, опционально, идентификатор файла в Redis

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя
        df : pd.DataFrame
            Данные для сохранения
        file_id : int, optional
            Идентификатор файла, связанного с DataFrame (по умолчанию None)
        """
        # Сериализация и сохранение DataFrame
        await cls.redis.set(f"{user_id}_data", pickle.dumps(df))
        if file_id is not None:
            # Сохранение идентификатора файла
            await cls.redis.set(f"{user_id}_file_id", pickle.dumps(file_id))

    @classmethod
    async def set_file_id(cls, user_id: str, file_id: int):
        """
        Сохраняет идентификатор файла в Redis

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя
        file_id : int
            Идентификатор файла
        """
        await cls.redis.set(f"{user_id}_file_id", pickle.dumps(file_id))

    @classmethod
    async def get_dataframe(cls, user_id: str) -> pd.DataFrame:
        """
        Извлекает DataFrame из Redis

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя

        Returns
        -------
        pd.DataFrame
            DataFrame, полученный из Redis

        Raises
        ------
        DataNotFound
            Если данные не найдены - ошибка
        """
        # Получение данных пользователя из Redis
        data = await cls.redis.get(f"{user_id}_data")
        if data is None:
            raise DataNotFound
        # Десериализация данных
        return pickle.loads(data)

    @classmethod
    async def get_filet_id(cls, user_id: str) -> int:
        """
        Извлекает идентификатор файла из Redis

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя

        Returns
        -------
        int
            Идентификатор файла

        Raises
        ------
        DataNotFound
            Если идентификатор файла не найден - ошибка
        """
        # Получение идентификатора файла из Redis
        file_id = await cls.redis.get(f"{user_id}_file_id")
        if file_id is None:
            raise DataNotFound
        # Десериализация идентификатора
        return pickle.loads(file_id)
