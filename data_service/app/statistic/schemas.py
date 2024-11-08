from enum import Enum
from pydantic import BaseModel
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


class ClusteringMethod(Enum):
    KMEANS = "kmeans"


class DataWithGroups(RequestDataBase):
    groups: list[dict[str, str | int]]
    include_nan: bool = True


class ParamsForOutliers(RequestDataBase):
    y_column: str | None = None
    method: OutliersMethod
    update_df: bool = False


class ParamsForCorrelation(BaseModel):
    left_columns: list[str]
    right_columns: list[str]
    method: CorrelationMethod
    round_value: int = 2
    dropna: bool = True


class ParamsForClusteringFast(RequestDataBase):
    n_clusters: int = 3


class ParamsForClustering(ParamsForClusteringFast):
    update_df: bool = False


class ParamsForOR(RequestDataBase):
    target_column: str
    split_column: str | None = None
