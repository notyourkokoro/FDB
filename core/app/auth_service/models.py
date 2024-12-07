"""Работа с моделями пользователя и группы осуществляется в модуле `auth_service`"""

from uuid import UUID
from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.storage_service.models import StorageFile


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    ORM-модель пользователя (таблица "users")
    """

    __tablename__ = "users"

    files: Mapped[list["StorageFile"]] = relationship(
        secondary="users_files",
        back_populates="users",
        cascade="all, delete",
    )

    groups: Mapped[list["Group"]] = relationship(
        secondary="users_groups",
        back_populates="users",
    )


class Group(Base):
    """
    ORM-модель пользовательной группы (таблица "groups")
    """

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(unique=True)

    users: Mapped[list["User"]] = relationship(
        secondary="users_groups", back_populates="groups"
    )

    files: Mapped[list["StorageFile"]] = relationship(
        secondary="groups_files",
        back_populates="groups",
        cascade="all, delete",
    )


class UserGroup(Base):
    """
    ORM-модель связи пользователя и группы (таблица "users_groups")
    """

    __tablename__ = "users_groups"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
