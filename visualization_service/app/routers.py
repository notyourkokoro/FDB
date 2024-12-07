from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import seaborn as sns

from app.schemas import (
    CorrelationMethod,
    ParamsForScatterplot,
    ParamsForScatterplotFast,
    ParamsForVisualizationCorrelation,
    ParamsForVisualizationCorrelationFast,
    ImageFormat,
)
from app.validation import CorrelationValidation, ValidateData
from app.dependencies import get_user_data
from app.utils import TempStorage
from app.builders import CorrelationBuilder

router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.post("/heatmap")
async def get_heatmap(
    params: ParamsForVisualizationCorrelation,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    data: dict = Depends(get_user_data),
) -> dict[str, dict[str, float | None]]:
    """
    Генерация тепловой карты для корреляционной матрицы

    Parameters
    ----------
    params : ParamsForVisualizationCorrelation
        Параметры для визуализации, такие как колонки и округление значений
    method : CorrelationMethod, optional
        Метод для получения корреляции (по умолчанию Spearman)
    data : dict
        Данные пользователя, которые будут
        использоваться для построения тепловой карты

    Returns
    -------
    dict
        Словарь, содержащий значения корреляции
    """
    # Валидация данных по указанным колонкам
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    # Построение корреляционной матрицы
    result = CorrelationBuilder.build(
        df=df, method=method, round_value=params.round_value, replace_nan=True
    )

    # Возвращение результата в виде словаря
    return result.to_dict()


@router.post("/heatmap/fast")
async def get_heatmap_fast(
    params: ParamsForVisualizationCorrelationFast,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    save_format: ImageFormat = ImageFormat.PNG,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Быстрая генерация тепловой карты для
    корреляционной матрицы в виде изображения

    Parameters
    ----------
    params : ParamsForVisualizationCorrelationFast
        Параметры для визуализации (включая название и параметры графика)
    method : CorrelationMethod, optional
        Метод для получения корреляции (по умолчанию Spearman)
    save_format : ImageFormat, optional
        Формат изображения для сохранения (по умолчанию PNG)
    data : dict
        Данные пользователя для построения тепловой карты

    Returns
    -------
    FileResponse
        Ответ, содержащий изображение тепловой карты
    """
    # Валидация данных по колонкам
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    # Построение корреляционной матрицы
    result = CorrelationBuilder.build(df=df, method=method)

    # Установка размеров фигуры
    fig_width = result.shape[1]  # Ширина зависит от количества столбцов
    fig_height = result.shape[0]  # Высота зависит от количества строк

    # Построение тепловой карты
    plt.figure(figsize=(fig_width, fig_height))
    sns.heatmap(
        result,
        annot=True,
        cmap="YlGnBu",  # Цветовая палитра
        cbar=params.cbar,  # Нужен ли цветовой бар?
        xticklabels=result.columns,
        yticklabels=result.index,
    )

    # Поворот подписей на оси X
    plt.xticks(rotation=params.x_lable_rotation)

    # Добавление заголовка, если он задан
    if params.title is not None:
        plt.title(params.title)

    # Сохранение изображения в файл и возвращение ссылки на него
    return TempStorage.return_file(save_format=save_format)


@router.post("/scatterplot")
async def get_scatterplot(
    params: ParamsForScatterplot,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Генерация диаграммы рассеяния (scatter plot) для выбранных колонок

    Parameters
    ----------
    params : ParamsForScatterplot
        Параметры для построения scatter plot
        (колонки для осей X и Y, опционально - hue, колонка,
        по которой будет осуществляться цветовое разделение данных)
    data : dict
        Данные пользователя для построения диаграммы

    Returns
    -------
    dict
        Словарь данных для scatter plot
    """
    # Основные колонки для осей X и Y
    columns = [params.x_column, params.y_column]
    # Добавление hue, если указано
    if params.hue_column is not None:
        columns.append(params.hue_column)

    # Валидация данных по выбранным колонкам
    df = ValidateData.check_columns(df=data["data"], columns=columns)

    # Возвращение диаграммы в формате словаря
    return df.to_dict()


@router.post("/scatterplot/fast")
async def get_scatterplot_fast(
    params: ParamsForScatterplotFast,
    save_format: ImageFormat = ImageFormat.PNG,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Быстрая генерация диаграммы рассеяния
    (scatter plot) в виде изображения

    Parameters
    ----------
    params : ParamsForScatterplotFast
        Параметры для построения scatter plot
    save_format : ImageFormat, optional
        Формат изображения для сохранения (по умолчанию PNG)
    data : dict
        Данные пользователя для построения диаграммы

    Returns
    -------
    FileResponse
        Ответ с изображением диаграммы рассеяния
    """
    # Основные колонки для осей X и Y
    columns = [params.x_column, params.y_column]
    # Добавление hue, если указано
    if params.hue_column is not None:
        columns.append(params.hue_column)

    # Валидация данных по выбранным колонкам
    df = ValidateData.check_columns(df=data["data"], columns=columns)

    # Построение scatter plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x=params.x_column,
        y=params.y_column,
        hue=params.hue_column,
        # Цветовая палитра
        palette="viridis",
        # Размер точек
        s=params.dot_size,
        # Отображение легенды, если нужно
        legend="auto" if params.need_legend is True else False,
    )

    # Подписи для осей
    plt.xlabel(params.x_column)
    plt.ylabel(params.y_column)

    # Добавление заголовка, если указан
    if params.title is not None:
        plt.title(params.title)

    # Сохранение изображения в файл и возвращение ссылки на него
    return TempStorage.return_file(save_format=save_format)
