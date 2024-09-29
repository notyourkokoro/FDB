from enum import Enum
from pydantic import Field

from app.schemas import RequestDataBase


class RecoveryMethod(Enum):
    KNN = 0


class DataForRecovery(RequestDataBase):
    method: RecoveryMethod
    n_neighbors: int | None = Field(gt=0, default=None)
