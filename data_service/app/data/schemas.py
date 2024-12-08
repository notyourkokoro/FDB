from enum import Enum
from pydantic import Field, BaseModel

from app.schemas import RequestDataBase


class RecoveryMethod(Enum):
    """
    Перечисление методов для восстановления данных

    Attributes
    ----------
    KNN : int
        Метод восстановления на основе K ближайших соседей
    """

    KNN = 0


class MergeMethod(Enum):
    """
    Перечисление методов для объединения данных

    Attributes
    ----------
    LEFT : str
        Метод объединения с сохранением всех данных из левой таблицы
    RIGHT : str
        Метод объединения с сохранением всех данных из правой таблицы
    OUTER : str
        Метод объединения с сохранением всех данных из обеих таблиц
    INNER : str
        Метод объединения с сохранением только совпадающих данных из обеих таблиц
    CROSS : str
        Метод объединения с сохранением всех возможных комбинаций строк из обеих таблиц
    """

    LEFT = "left"
    RIGHT = "right"
    OUTER = "outer"
    INNER = "inner"
    CROSS = "cross"


class ParamsForRecovery(RequestDataBase):
    """
    Схема для восстановления данных

    Attributes
    ----------
    method : RecoveryMethod
        Метод восстановления данных
    n_neighbors : int | None
        Количество соседей для метода KNN (если указан метод KNN)
    update_df : bool
        Флаг обновления данных в Redis
    """

    method: RecoveryMethod
    n_neighbors: int | None = Field(gt=0, default=None)
    update_df: bool = False


class ParamsForExpr(BaseModel):
    """
    Схема для работы с выражениями
    (например, для создание вычисляего поля)

    Attributes
    ----------
    expr : str
        Строка с выражением
    update_df : bool
        Флаг обновления данных в Redis
    """

    expr: str
    update_df: bool = False


class ParamsForCalculate(ParamsForExpr):
    """
    Схема для создания вычисляемого поля

    Attributes
    ----------
    column_name : str
        Название столбца для сохранения результата вычислений
    rewrite : bool
        Флаг перезаписи существующего столбца с таким же названием
    convert_bool : bool
        Флаг конвертации булевых значений в числовые (False: 0, True: 1)
    """

    column_name: str
    rewrite: bool = False
    convert_bool: bool = True


class ParamsForSelect(RequestDataBase):
    """
    Схема для выбора столбцов данных

    Attributes
    ----------
    update_df : bool
        Флаг обновления данных в Redis
    """

    update_df: bool = False


class ParamsForMerge(BaseModel):
    """
    Схема для объединения текущих данных с другим файлом

    Attributes
    ----------
    left_columns : list[str]
        Список столбцов, участвующих в объединении,
        для текущего DataFrame (хранится в Redis)
    right_columns : list[str]
        Список столбцов, участвующих в объединении,
        для данных из другого файла, с которым
        пользователь хочет объединить текущий DataFrame
    right_sep : str | None
        Разделитель для данных из правой таблицы
        (если загружается CSV-файл)
    other_file_id : int
        Идентификатор другого файла для объединения
    update_df : bool
        Флаг обновления данных в Redis
    """

    left_columns: list[str]
    right_columns: list[str]
    right_sep: str | None = None
    other_file_id: int
    update_df: bool = False
