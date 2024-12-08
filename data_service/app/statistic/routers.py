import pandas as pd

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.dependencies import get_user_data
from app.statistic.schemas import (
    ClusteringMethod,
    ParamsForClustering,
    ParamsForClusteringFast,
    ParamsForCorrelation,
    ParamsForOR,
    ParamsForOutliers,
    DataWithGroups,
)
from app.statistic.builders import (
    ClustersBuilder,
    CorrBuilder,
    DescriptiveStatisticsBuilder,
    ORBuilder,
    OutliersBuilder,
)
from app.data.builders import DataBuilder
from app.utils import TempStorage
from app.validation import ValidateData
from app.exceptions import ColumnsDuplicateException, ColumnsNotFoundException
from app.schemas import DataFormat
from app.memory import RedisConnection


# Создание роутера для работы со статистикой
router = APIRouter(prefix="/statistic", tags=["statistic"])


@router.post("/descriptive")
async def get_descriptive_statistics(
    params: DataWithGroups,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Получение описательной статистики для данных с учетом групп

    Parameters
    ----------
    params : DataWithGroups
        Параметры для группировки и
        вычисления описательной статистики
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Таблица с описательной статистика в виде
        словаря, где ключи - названия столбцов
    """
    # Проверка DataFrame на наличия необходимых столбцов
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    # Генерация описательной статистики
    datas = DataBuilder.build(df=df, groups=params.groups)

    return DescriptiveStatisticsBuilder.build(
        datas=datas, include_nan=params.include_nan
    )


@router.post("/descriptive/fast")
async def get_fast_descriptive_statistics(
    params: DataWithGroups,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Получение описательной статистики для
    данных с учетом групп в виде файла

    Parameters
    ----------
    params : DataWithGroups
        Параметры для группировки и вычисления статистики
    save_format : DataFormat
        Формат сохранения файла с результом (по умолчанию XLSX)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Файл с описательной статистикой
    """
    result = await get_descriptive_statistics(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.post("/outliers")
async def get_outliers(
    params: ParamsForOutliers,
    data: dict = Depends(get_user_data),
) -> dict[str, list[int]]:
    """
    Нахождение выбросов в данных
    на основе выбранных столбцов

    Parameters
    ----------
    params : ParamsForOutliers
        Параметры для поиска выбросов
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict[str, list[int]]
        Результат поиска выбросов
    """
    # Проверка DataFrame на наличия необходимых столбцов
    y_column = params.y_column
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    if y_column is not None and y_column not in df.columns:
        raise ColumnsNotFoundException([y_column])

    # Поиск выбросов
    result = OutliersBuilder.build(
        df=df,
        method_name=str.lower(params.method.name),
        y_column=y_column,
    )

    # Обновление DataFrame в Redis, если это требуется
    if params.update_df is True:
        df = data["data"].assign(**result)
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return result


@router.post("/outliers/fast")
async def get_outliers_fast(
    params: ParamsForOutliers,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Нахождение выбросов в данных
    на основе выбранных столбцов
    с возвратом результата в виде файла

    Parameters
    ----------
    params : ParamsForOutliers
        Параметры для поиска выбросов
    save_format : DataFormat
        Формат сохранения результата (по умолчанию XLSX)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Файл с результатами поиска выбросов
    """
    # Поиск выбросов
    result = await get_outliers(params=params, data=data)
    # Добавление к текущему DataFrame данных о выбросах
    df = data["data"]
    if len(params.columns) != 0:
        df = df[params.columns]
    df = df.assign(**result)

    return TempStorage.return_file(df=df, save_format=save_format)


@router.post("/correlation")
async def get_correlation(
    params: ParamsForCorrelation,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Получение таблицы с корреляцией

    Parameters
    ----------
    params : ParamsForCorrelation
        Параметры для вычисления корреляции
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Результат вычисления корреляции
    """
    # Проверка DataFrame на наличия дубликатов столбцов в левых и правых колонках
    if set(params.left_columns) & set(params.right_columns):
        raise ColumnsDuplicateException(
            columns=list(set(params.left_columns) & set(params.right_columns))
        )

    # Проверка DataFrame на наличия необходимых столбцов
    df = ValidateData.check_columns(
        df=data["data"], columns=(params.left_columns + params.right_columns)
    )
    # Получение данных с корреляцией
    result = CorrBuilder.build(
        df=df,
        left_columns=params.left_columns,
        right_columns=params.right_columns,
        round_value=params.round_value,
        dropna=params.dropna,
    )
    return result.to_dict()


@router.post("/correlation/fast")
async def get_correlation_fast(
    params: ParamsForCorrelation,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Получение таблицы с корреляцией
    в виде файла

    Parameters
    ----------
    params : ParamsForCorrelation
        Параметры для вычисления корреляции
    save_format : DataFormat
        Формат сохранения результата (по умолчанию XLSX)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Файл с результатами корреляции
    """
    result = await get_correlation(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.post("/clustering")
async def get_clusters(
    params: ParamsForClustering,
    method: ClusteringMethod = ClusteringMethod.KMEANS,
    data: dict = Depends(get_user_data),
) -> dict:
    """
    Классификация данных

    Parameters
    ----------
    params : ParamsForClustering
        Параметры для кластеризации
    method : ClusteringMethod
        Метод кластеризации (по умолчанию KMEANS)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Результат кластеризации
    """
    # Проверка DataFrame на наличия необходимых столбцов
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    # Проверка столбов DataFrame на числовой тип данных
    ValidateData.check_numeric_type(df, df.columns)

    # Кластеризация
    result = ClustersBuilder.build(df=df, method=method, n_clusters=params.n_clusters)
    # Обновление DataFrame в Redis, если это требуется
    if params.update_df is True:
        df = data["data"].assign(**result)
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return result


@router.post("/clustering/fast")
async def get_clusters_fast(
    params: ParamsForClusteringFast,
    method: ClusteringMethod = ClusteringMethod.KMEANS,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Классификация данных с получением
    результата в виде файла

    Parameters
    ----------
    params : ParamsForClusteringFast
        Параметры для кластеризации
    method : ClusteringMethod
        Метод кластеризации (по умолчанию KMEANS)
    save_format : DataFormat
        Формат сохранения результата (по умолчанию XLSX)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Файл с результатами кластеризации
    """
    # Проверка DataFrame на наличия необходимых столбцов
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    # Проверка столбов DataFrame на числовой тип данных
    ValidateData.check_numeric_type(df, df.columns)

    # Кластеризация
    result = ClustersBuilder.build(df=df, method=method, n_clusters=params.n_clusters)

    return TempStorage.return_file(
        df=data["data"].assign(**result), save_format=save_format
    )


@router.post("/or")
async def get_or_table(
    params: ParamsForOR, data: dict = Depends(get_user_data)
) -> dict:
    """
    Получение таблицы с OR и 95% CI

    Parameters
    ----------
    params : ParamsForOR
        Параметры для вычисления OR
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Результат вычисления
    """
    params_columns = [params.target_column]
    if params.split_column is not None:
        params_columns.append(params.split_column)

    # Опредление столбцов в DataFrame
    if params.columns:
        main_columns = params.columns
    else:
        main_columns = data["data"].columns.to_list()

    columns = list(frozenset(main_columns + params_columns))

    # Проверка DataFrame на наличия необходимых столбцов
    df = ValidateData.check_columns(df=data["data"], columns=columns)

    # Получение таблицы с OR и 95% CI
    builder = ORBuilder(
        df=df, target_column=params_columns[0], split_column=params_columns[-1]
    )

    return builder.build()


@router.post("/or/fast")
async def get_or_table_fast(
    params: ParamsForOR,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    """
    Получение таблицы с OR и 95% CI в виде файла

    Parameters
    ----------
    params : ParamsForOR
        Параметры для вычисления OR
    save_format : DataFormat
        Формат сохранения результата (по умолчанию XLSX)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Файл с таблицей OR
    """
    result = await get_or_table(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)
