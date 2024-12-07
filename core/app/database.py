from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings import settings

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Базовая ORM-модель, от которой наследуются остальные
    """

    pass


class AsyncDataBase:
    """
    Ассихронное соединение с базой данных
    """

    def __init__(self, url: str, echo: bool):
        """
        Создание ассихронного соединения с базой данных

        Parameters
        ----------
        url : str
            Строка подключения к базе данных
        echo : bool
            Признак отображения SQL-запросов
        """
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Получение ассихронной сессии

        Returns
        -------
        AsyncGenerator[AsyncSession, None]
            Генератор ассихронных сессий
        """
        async with self.session_factory() as session:
            yield session


# Инициализация ассихронного соединения с БД
async_db = AsyncDataBase(
    url=settings.db_url,
    echo=settings.echo,
)
