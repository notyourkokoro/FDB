from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.database import async_db


async def get_user_db(
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Возвращает ассинхронное получение к базе данных для работы с FastAPI Users

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия SQLAlchemy, создаваемая через Depends

    Yields
    ------
    SQLAlchemyUserDatabase
        Ассинхронное получение к базе данных для работы с FastAPI Users
    """
    yield SQLAlchemyUserDatabase(session, User)
