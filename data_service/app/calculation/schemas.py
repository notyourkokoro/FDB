from enum import Enum
from pydantic import BaseModel, Field


class BMIDescription(Enum):
    """
    Перечисление с описанием групп BMI
    """

    A = "Выраженный дефицит массы тела"
    B = "Недостаточная (дефицит) масса тела"
    C = "Норма"
    D = "Избыточная масса тела (предожирение)"
    E = "Ожирение первой степени"
    F = "Ожирение второй степени"
    G = "Ожирение третьей степени"


class ParamsForBMI(BaseModel):
    """
    Схема для параметров, используемых при расчете BMI

    Attributes
    ----------
    m_column : str
        Название колонки с массой тела в килограммах
    h_column : str
        Название колонки с ростом в метрах
    round_value : int
        Количество знаков после запятой для округления
        значения BMI (по умолчанию 2)
    groups : bool
        Флаг, указывающий, нужно ли добавлять группы BMI
        в результат (по умолчанию False)
    need_save : bool
        Флаг, указывающий, нужно ли сохранять результат
        расчета в текущем DataFrame (по умолчанию False)
    """

    m_column: str = Field(description="Масса в килограммах")
    h_column: str = Field(description="Рост в метрах")
    round_value: int = 2
    groups: bool = False
    need_save: bool = False
