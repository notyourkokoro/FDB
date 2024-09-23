from pydantic import BaseModel


class DataBase(BaseModel):
    columns: list[str] = []


class DataWithGroups(DataBase):
    groups: list[dict[str, str | int]]
    include_nan: bool = True
