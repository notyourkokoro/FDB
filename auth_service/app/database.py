from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.settings import settings

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class AsyncDataBase:
    def __init__(self, url: str, echo: bool):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, expire_on_commit=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session


async_db = AsyncDataBase(
    url=settings.db_url,
    echo=settings.echo,
)
