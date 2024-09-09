from uuid import UUID
from enum import Enum

from datetime import datetime

from sqlalchemy import ForeignKey, func

from sqlalchemy.orm import Mapped, mapped_column, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from app.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    files: Mapped[list["StorageFile"]] = relationship(
        secondary="users_files",
        back_populates="users",
        cascade="all, delete",
    )


class FileTypeEnum(Enum):
    csv = 1
    xlsx = 2
    xls = 3


class FileType(Base):
    __tablename__ = "file_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class StorageFile(Base):
    __tablename__ = "storage_files"

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    creator_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    filename: Mapped[str]
    path: Mapped[str]
    size: Mapped[int]
    type_id: Mapped[int] = mapped_column(ForeignKey("file_types.id"))
    upload_date: Mapped[datetime] = mapped_column(
        default=datetime.now, server_default=func.now()
    )
    update_date: Mapped[datetime] = mapped_column(
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.now(),
        server_onupdate=func.now(),
    )

    users: Mapped[list["User"]] = relationship(
        secondary="users_files", back_populates="files", passive_deletes=True
    )

    def __repr__(self):
        return "{name}(id={id}, name={filename})".format(
            name=self.__class__.__name__,
            id=self.id,
            filename=self.filename,
        )


class UserFile(Base):
    __tablename__ = "users_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    file_id: Mapped[int] = mapped_column(
        ForeignKey("storage_files.id", ondelete="CASCADE")
    )
