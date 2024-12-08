from enum import Enum
from pydantic import BaseModel
from app.schemas import RequestDataBase


class OutliersMethod(Enum):
    """
    Перечисление методов для
    обнаружения выбросов в данных

    Attributes
    ----------
    Z_SCORE : int
        Метод Z-оценки
    MODIFIED_Z_SCORE : int
        Модифицированный Z-метод для более
        устойчивого обнаружения выбросов
    IQR : int
        Метод межквартильного размаха (IQR)
    ISO_FOREST : int
        Метод изолированного леса (Isolation Forest)
    """

    Z_SCORE = 0
    MODIFIED_Z_SCORE = 1
    IQR = 2
    ISO_FOREST = 3


class CorrelationMethod(Enum):
    """
    Перечисление методов для вычисления
    корреляции между столбцами

    Attributes
    ----------
    PEARSON : int
        Метод корреляции Пирсона для
        вычисления линейной зависимости
    KENDALL : int
        Метод корреляции Кендалла для
            вычисления ранговой зависимости
    SPEARMAN : int
        Метод корреляции Спирмена для
        вычисления монотонной зависимости
    """

    PEARSON = 0
    KENDALL = 1
    SPEARMAN = 2


class ClusteringMethod(Enum):
    """
    Перечисление методов кластеризации данных

    Attributes
    ----------
    KMEANS : str
        Метод кластеризации K-средних (KMeans)
    """

    KMEANS = "kmeans"


class DataWithGroups(RequestDataBase):
    """
    Схема для работы с данными с разделением по группам

    Attributes
    ----------
    groups : list[dict[str, str | int]]
        Список групп с параметрами фильтрации данных
    include_nan : bool
        Флаг включения или исключения значений NaN в группах
    """

    groups: list[dict[str, str | int]]
    include_nan: bool = True


class ParamsForOutliers(RequestDataBase):
    """
    Схема для обнаружения выбросов в данных

    Attributes
    ----------
    y_column : str | None
        Название столбца, по которому будут
        вычисляться выбросы (опционально).
        Если не указано, то выбросы будут
        вычисляться по всем столбцам
    method : OutliersMethod
        Метод обнаружения выбросов
    update_df : bool
        Флаг обновления DataFrame в Redis
    """

    y_column: str | None = None
    method: OutliersMethod
    update_df: bool = False


class ParamsForCorrelation(BaseModel):
    """
    Схема для вычисления корреляции
    между столбцами в DataFrame

    Attributes
    ----------
    left_columns : list[str]
        Список столбцов, которые будут
        образовывать пары с правыми столбцами
    right_columns : list[str]
        Список столбцов, которые будут
        образовывать пары с левыми столбцами
    method : CorrelationMethod
        Метод вычисления корреляции
    round_value : int
        Количество знаков после запятой для
        округления значений корреляции
    dropna : bool
        Флаг удаления строк с NaN значениями
        перед расчетом корреляции
    """

    left_columns: list[str]
    right_columns: list[str]
    method: CorrelationMethod
    round_value: int = 2
    dropna: bool = True


class ParamsForClusteringFast(RequestDataBase):
    """
    Схема для кластеризации данных с
    последующим получением DataFrame в виде файла

    Attributes
    ----------
    n_clusters : int
        Количество кластеров для разделения данных
    """

    n_clusters: int = 3


class ParamsForClustering(ParamsForClusteringFast):
    """
    Схема для кластеризации данных

    Attributes
    ----------
    update_df : bool
        Флаг обновления DataFrame в Redis
    """

    update_df: bool = False


class ParamsForOR(RequestDataBase):
    """
    Схема для созданиея таблицы с OR и 95% CI

    Attributes
    ----------
    target_column : str
        Целевой столбец
    split_column : str | None
        Столбец, по которому будет выполняться разделение
    """

    target_column: str
    split_column: str | None = None
