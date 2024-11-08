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


router = APIRouter(prefix="/statistic", tags=["statistic"])


@router.post("/descriptive")
async def get_descriptive_statistics(
    params: DataWithGroups,
    data: dict = Depends(get_user_data),
) -> dict:
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
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
    result = await get_descriptive_statistics(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.post("/outliers")
async def get_outliers(
    params: ParamsForOutliers,
    data: dict = Depends(get_user_data),
) -> dict[str, list[int]]:
    """
    columns (list[str]): срез данных по столбцам, в котором будут
    искаться выбросы / на которых будет строиться модель
    """
    y_column = params.y_column
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    if y_column is not None and y_column not in df.columns:
        raise ColumnsNotFoundException([y_column])

    result = OutliersBuilder.build(
        df=df,
        method_name=str.lower(params.method.name),
        y_column=y_column,
    )

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
    result = await get_outliers(params=params, data=data)
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
    if set(params.left_columns) & set(params.right_columns):
        raise ColumnsDuplicateException(
            columns=list(set(params.left_columns) & set(params.right_columns))
        )

    df = ValidateData.check_columns(
        df=data["data"], columns=(params.left_columns + params.right_columns)
    )
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
    result = await get_correlation(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.post("/clustering")
async def get_clusters(
    params: ParamsForClustering,
    method: ClusteringMethod = ClusteringMethod.KMEANS,
    data: dict = Depends(get_user_data),
) -> dict:
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    ValidateData.check_numeric_type(df, df.columns)

    result = ClustersBuilder.build(df=df, method=method, n_clusters=params.n_clusters)
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
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    ValidateData.check_numeric_type(df, df.columns)

    result = ClustersBuilder.build(df=df, method=method, n_clusters=params.n_clusters)

    return TempStorage.return_file(
        df=data["data"].assign(**result), save_format=save_format
    )


@router.post("/or")
async def get_or_table(
    params: ParamsForOR, data: dict = Depends(get_user_data)
) -> dict:
    params_columns = [params.target_column]
    if params.split_column is not None:
        params_columns.append(params.split_column)

    if params.columns:
        main_columns = params.columns
    else:
        main_columns = data["data"].columns.to_list()

    columns = list(frozenset(main_columns + params_columns))

    df = ValidateData.check_columns(df=data["data"], columns=columns)

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
    result = await get_or_table(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)
