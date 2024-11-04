from fastapi import APIRouter, Depends
import pandas as pd

from app.validation import ValidateData
from app.dependencies import get_user_data
from app.calculation.utils import calculate_bmi_group
from app.calculation.schemas import BMIDescription, ParamsForBMI
from app.memory import RedisConnection

router = APIRouter(prefix="/calculation", tags=["calculation"])


@router.get("/bmi/simple")
async def get_bmi_simple(m: float, h: float, description: bool = False) -> dict:
    """
    Вычисление ИМТ

    Args:
        m (float): рост в метрах
        h (float): вес в килограммах
        description (bool, optional): True - необходимо ли описание BMI
    """
    h = h / 100 if h > 100 else h
    bmi = m / h**2

    description_text = ""
    if description is True:
        group = calculate_bmi_group(bmi)
        description_text = getattr(BMIDescription, chr(group + 64)).value

    return {"bmi": bmi, "description": description_text}


@router.post("/bmi/dataframe")
async def get_bmi_full(
    params: ParamsForBMI,
    data: dict = Depends(get_user_data),
) -> dict:
    df = ValidateData.check_columns(
        df=data["data"], columns=[params.m_column, params.h_column]
    )

    result = pd.DataFrame()
    result["BMI"] = round(
        df[params.m_column] / ((df[params.h_column] / 100) ** 2), params.round_value
    )

    columns_to_save = ["BMI"]

    if params.groups is True:
        result["BMI_group"] = result["BMI"].apply(calculate_bmi_group)
        columns_to_save.append("BMI_group")

    if params.need_save is True:
        df = data["data"]
        for col in columns_to_save:
            df[col] = result[col]
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return result.to_dict()
