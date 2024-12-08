from fastapi import APIRouter, Depends
import pandas as pd

from app.validation import ValidateData
from app.dependencies import get_user_data
from app.calculation.utils import calculate_bmi_group
from app.calculation.schemas import BMIDescription, ParamsForBMI
from app.memory import RedisConnection

# Создание маршрутизатора с префиксом и тегами для группы эндпоинтов
router = APIRouter(prefix="/calculation", tags=["calculation"])


@router.get("/bmi/simple")
async def get_bmi_simple(m: float, h: float, description: bool = False) -> dict:
    """
    Расчет простого BMI

    Parameters
    ----------
    m : float
        Масса тела в килограммах
    h : float
        Рост в сантиметрах или метрах
    description : bool
        Флаг, указывающий, нужно ли возвращать текстовое описание группы BMI

    Returns
    -------
    dict
        Словарь с рассчитанным BMI и текстовым описанием (если указано)
    """
    # Конвертация роста из сантиметров в метры, если значение больше 100
    h = h / 100 if h > 100 else h
    # Вычисление BMI по формуле: масса / (рост^2)
    bmi = m / h**2

    description_text = ""
    if description is True:
        # Определение группы BMI и получение текстового описания
        group = calculate_bmi_group(bmi)
        description_text = getattr(BMIDescription, chr(group + 64)).value

    return {"bmi": bmi, "description": description_text}


@router.post("/bmi/dataframe")
async def get_bmi_full(
    params: ParamsForBMI,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Расчет BMI на основе табличных данных

    Parameters
    ----------
    params : ParamsForBMI
        Параметры для расчета BMI, включая названия колонок и основные параметры
    data : dict
        Данные пользователя, получаемые из Redis

    Returns
    -------
    dict
        Словарь с результатами расчета BMI (включая группы, если указано)
    """
    # Проверка наличия необходимых колонок в данных пользователя
    df = ValidateData.check_columns(
        df=data["data"], columns=[params.m_column, params.h_column]
    )

    # Создание результирующего DataFrame для расчетов
    result = pd.DataFrame()
    # Расчет BMI для каждой строки с округлением до указанного значения
    result["BMI"] = round(
        df[params.m_column] / ((df[params.h_column] / 100) ** 2), params.round_value
    )

    # Список колонок, которые нужно сохранить
    columns_to_save = ["BMI"]

    if params.groups is True:
        # Если требуется определить группы BMI, добавление их в результат
        result["BMI_group"] = result["BMI"].apply(calculate_bmi_group)
        columns_to_save.append("BMI_group")

    if params.need_save is True:
        # Если требуется сохранить данные, обновление исходного DataFrame
        df = data["data"]
        for col in columns_to_save:
            df[col] = result[col]
        # Сохранение обновленного DataFrame в Redis
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    # Преобразование DataFrame в словарь и его возвращение
    return result.to_dict()
