from enum import Enum
from pydantic import Field, BaseModel

from app.schemas import RequestDataBase


class RecoveryMethod(Enum):
    KNN = 0


class DataForRecovery(RequestDataBase):
    method: RecoveryMethod
    n_neighbors: int | None = Field(gt=0, default=None)


class DataForCalculate(BaseModel):
    column_name: str
    expr: str
    rewrite: bool = False
    update_df: bool = True
    convert_bool: bool = True
