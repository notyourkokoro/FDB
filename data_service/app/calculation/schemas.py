from enum import Enum
from pydantic import BaseModel, Field


class BMIDescription(Enum):
    A = "Выраженный дефицит массы тела"
    B = "Недостаточная (дефицит) масса тела"
    C = "Норма"
    D = "Избыточная масса тела (предожирение)"
    E = "Ожирение первой степени"
    F = "Ожирение второй степени"
    G = "Ожирение третьей степени"


class ParamsForBMI(BaseModel):
    m_column: str = Field(description="Масса в килограммах")
    h_column: str = Field(description="Рост в метрах")
    round_value: int = 2
    groups: bool = False
    need_save: bool = False
