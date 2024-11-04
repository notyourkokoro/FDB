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


class ParamsForVisualizationCorrelation(BaseModel):
    columns: list[str] = []
    round_value: int = 2


class ParamsForVisualizationFast(BaseModel):
    title: str | None = None


class ParamsForVisualizationCorrelationFast(
    ParamsForVisualizationCorrelation, ParamsForVisualizationFast
):
    cbar: bool = True
    x_lable_rotation: int = 0


class ParamsForScatterplot(BaseModel):
    x_column: str
    y_column: str
    hue_column: str | None = None


class ParamsForScatterplotFast(ParamsForScatterplot, ParamsForVisualizationFast):
    dot_size: int = 100
    need_legend: bool = False
