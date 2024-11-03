from enum import Enum
from pydantic import BaseModel


class ImageFormat(Enum):
    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"


class ImageMediaType(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"


class CorrelationMethod(Enum):
    PEARSON = "pearson"
    KENDALL = "kendall"
    SPEARMAN = "spearman"


class DataForVisualizationCorrelation(BaseModel):
    columns: list[str] = []
    round_value: int = 2


class DataForVisualizationFast(BaseModel):
    title: str | None
    x_lable_rotation: int = 0


class DataForVisualizationCorrelationFast(DataForVisualizationFast):
    columns: list[str] = []
    cbar: bool = True
