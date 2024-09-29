from pydantic import BaseModel


class RequestDataBase(BaseModel):
    columns: list[str] = []
