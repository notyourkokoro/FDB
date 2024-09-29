from enum import Enum
from pydantic import BaseModel


class DataFormat(Enum):
    CSV = "csv"
    XLSX = "xlsx"


class DataMediaType(Enum):
    CSV = "text/csv"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class RequestDataBase(BaseModel):
    columns: list[str] = []
