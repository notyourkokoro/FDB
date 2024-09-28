from enum import Enum
from pydantic import BaseModel


class OutliersMethod(Enum):
    Z_SCORE = 0
    MODIFIED_Z_SCORE = 1
    IQR = 2
    ISO_FOREST = 3


class DataBase(BaseModel):
    columns: list[str] = []


class DataWithGroups(DataBase):
    groups: list[dict[str, str | int]]
    include_nan: bool = True


class DataForOutliers(DataBase):
    y_column: str | None = None
    method: OutliersMethod
