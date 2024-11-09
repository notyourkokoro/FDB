from fastapi_users.db import SQLAlchemyBaseUserTableUUID


from app.database import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    pass