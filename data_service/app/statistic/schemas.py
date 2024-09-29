from enum import Enum

from app.schemas import RequestDataBase


class OutliersMethod(Enum):
    Z_SCORE = 0
    MODIFIED_Z_SCORE = 1
    IQR = 2
    ISO_FOREST = 3


class CorrelationMethod(Enum):
    PEARSON = 0
    KENDALL = 1
    SPEARMAN = 2


class DataWithGroups(RequestDataBase):
    groups: list[dict[str, str | int]]
    include_nan: bool = True


class DataForOutliers(RequestDataBase):
    y_column: str | None = None
    method: OutliersMethod


class DataForCorrelation(RequestDataBase):
    method: CorrelationMethod
    round_value: int = 2
