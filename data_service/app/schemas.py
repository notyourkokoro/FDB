from enum import Enum
from pydantic import BaseModel


class DataFormat(Enum):
    """
    Перечисление форматов данных,
    которые поддерживает сервис
    """

    CSV = "csv"
    XLSX = "xlsx"


class DataMediaType(Enum):
    """
    Перечисление типов медиа-файлов,
    которые поддерживает сервис
    """

    CSV = "text/csv"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class RequestDataBase(BaseModel):
    """
    Схема базового запроса

    Attributes
    ----------
    columns : list[str]
        Список названий колонок
    """

    columns: list[str] = []
