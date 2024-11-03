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
    title: str | None = None


class DataForVisualizationCorrelationFast(
    DataForVisualizationCorrelation, DataForVisualizationFast
):
    cbar: bool = True
    x_lable_rotation: int = 0


class DataForScatterplot(BaseModel):
    x_column: str
    y_column: str
    hue_column: str | None = None


class DataForScatterplotFast(DataForScatterplot, DataForVisualizationFast):
    dot_size: int = 100
    need_legend: bool = False
