from enum import Enum
from pydantic import BaseModel


class ImageFormat(Enum):
    """
    Перечисление форматов изображений,
    которые поддерживаются для сохранения
    """

    PNG = "png"
    JPEG = "jpeg"
    TIFF = "tiff"


class ImageMediaType(Enum):
    """
    Перечисление типов медиаконтента
    для различных форматов изображений
    """

    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"


class CorrelationMethod(Enum):
    """
    Перечисление методов корреляции,
    которые могут быть использованы
    для анализа данных
    """

    PEARSON = "pearson"
    KENDALL = "kendall"
    SPEARMAN = "spearman"


class ParamsForVisualizationCorrelation(BaseModel):
    """
    Схема данных для параметров,
    необходимых для визуализации корреляции

    Attributes
    ----------
    columns : list[str]
        Список колонок, для которых будет строиться матрица с корреляцией
    round_value : int
        Количество знаков после запятой при округлении значений корреляции
    """

    columns: list[str] = []
    round_value: int = 2


class ParamsForVisualizationFast(BaseModel):
    """
    Базовая схема для параметров визуализации,
    которая может быть расширена другими моделями

    Attributes
    ----------
    title : str | None
        Заголовок для визуализации (опционально)
    """

    title: str | None = None


class ParamsForVisualizationCorrelationFast(
    ParamsForVisualizationCorrelation, ParamsForVisualizationFast
):
    """
    Схема данных для параметров визуализации матрицы с
    корреляцией с дополнительными опциями для отображения

    Attributes
    ----------
    cbar : bool
        Включить или выключить цветовую шкалу на тепловой карте (по умолчанию True)
    x_lable_rotation : int
        Угол поворота подписей оси X (по умолчанию 0)
    """

    cbar: bool = True
    x_lable_rotation: int = 0


class ParamsForScatterplot(BaseModel):
    """
    Схема данных для параметров диаграммы рассеяния

    Attributes
    ----------
    x_column : str
        Колонка для оси X
    y_column : str
        Колонка для оси Y
    hue_column : str | None
        Колонка для окраски точек (опционально)
    """

    x_column: str
    y_column: str
    hue_column: str | None = None


class ParamsForScatterplotFast(ParamsForScatterplot, ParamsForVisualizationFast):
    """
    Схема данных для быстрого создания диаграммы рассеяния
    с дополнительными параметрами визуализации

    Attributes
    ----------
    dot_size : int
        Размер точек на диаграмме рассеяния (по умолчанию 100)
    need_legend : bool
        Параметр для отображения легенды (по умолчанию False)
    """

    dot_size: int = 100
    need_legend: bool = False
