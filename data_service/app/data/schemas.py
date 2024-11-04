from enum import Enum
from pydantic import Field, BaseModel

from app.schemas import RequestDataBase


class RecoveryMethod(Enum):
    KNN = 0


class ParamsForRecovery(RequestDataBase):
    method: RecoveryMethod
    n_neighbors: int | None = Field(gt=0, default=None)
    update_df: bool = False


class ParamsForExpr(BaseModel):
    expr: str
    update_df: bool = False


class ParamsForCalculate(ParamsForExpr):
    column_name: str
    rewrite: bool = False  # перезаписать колонку с таким именем
    convert_bool: bool = True


class ParamsForSelect(RequestDataBase):
    update_df: bool = False
