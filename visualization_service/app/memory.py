import pandas as pd
import pickle
import redis.asyncio as redis

from app.settings import settings
from app.exceptions import DataNotFound


class RedisConnection:
    """
    Класс для управления соединением с Redis

    Parameters
    ----------
    redis : redis.asyncio.Redis | None
        Объект соединения с Redis
    """

    redis = None

    @classmethod
    async def connect(cls):
        """
        Устанавливает соединение с Redis сервером

        Попытка подключиться к серверу Redis, если соединение еще не установлено.
        Если соединение не удалось, выводится ошибка
        """
        # Если соединение с Redis еще не установлено - создаем
        if cls.redis is None:
            cls.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        try:
            # Проверка доступа к Redis с помощью команды ping
            await cls.redis.ping()
        except Exception as error:
            # Вывод сообщение в случае ошибки подключения
            print("Неудачная попытка подключиться к Redis: {error}".format(error=error))

    @classmethod
    async def disconnect(cls):
        """
        Закрывает соединение с Redis сервером

        Завершается работа с Redis, выполняя разрыв соединения.
        При возникновении ошибки при отключении, выводится сообщение об ошибке.
        """
        # Если соединение с Redis установлено, тогда закрываем
        if redis is not None:
            try:
                # Закрываем соединение с Redis
                await cls.redis.aclose()
            except Exception as error:
                # Вывод сообщения об ошибки, если произошла проблема при разрыве соединения
                print(
                    "Произошла ошибка при разрыве соединения с Redis: {error}".format(
                        error=error
                    )
                )

    @classmethod
    async def get_dataframe(cls, user_id: str) -> pd.DataFrame:
        """
        Извлекает загруженные пользователем данные из Redis

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя, данные которого нужно получить

        Returns
        -------
        pd.DataFrame
            Данные пользователя в виде DataFrame

        Raises
        ------
        DataNotFound
            Если данные не найдены в Redis - ошибка об отсутствии ранее загруженных данных
        """
        # Получение сериализованных данные пользователя из Redis по ключу
        data = await cls.redis.get(f"{user_id}_data")
        # Если данные не найдены, рейсится исключение
        if data is None:
            raise DataNotFound
        # Возвращение десериализованные данные в виде pandas DataFrame
        return pickle.loads(data)
