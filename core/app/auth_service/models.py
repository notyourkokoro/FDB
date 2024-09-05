from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from sqlalchemy.orm import Mapped, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.storage_service.models import StorageFile


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    files: Mapped[list["StorageFile"]] = relationship(
        secondary="users_files",
        back_populates="users",
        cascade="all, delete",
    )
