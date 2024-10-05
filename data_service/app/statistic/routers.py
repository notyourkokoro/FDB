import pandas as pd

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.dependencies import get_user_data
from app.statistic.schemas import DataForCorrelation, DataForOutliers, DataWithGroups
from app.statistic.builders import (
    CorrBuilder,
    DataBuilder,
    DescriptiveStatisticsBuilder,
    OutliersBuilder,
)
from app.utils import ValidateData, TempStorage
from app.exceptions import ColumnsDuplicateException, ColumnsNotFoundException
from app.schemas import DataFormat


router = APIRouter(prefix="/statistic", tags=["statistic"])


@router.post("/descriptive")
async def get_descriptive_statistics(
    params: DataWithGroups,
    data=Depends(get_user_data),
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
    data=Depends(get_user_data),
) -> FileResponse:
    result = await get_descriptive_statistics(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.post("/outliers")
async def get_outliers(
    params: DataForOutliers,
    data=Depends(get_user_data),
) -> dict[str, list[int]]:
    """
    columns (list[str]): срез данных по столбцам, в котором будут
    искаться выбросы / на которых будет строиться модель
    """
    y_column = params.y_column
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    if y_column is not None and y_column not in df.columns:
        raise ColumnsNotFoundException([y_column])

    return OutliersBuilder.build(
        df=df,
        method_name=str.lower(params.method.name),
        y_column=y_column,
    )


@router.post("/outliers/fast")
async def get_outliers_fast(
    params: DataForOutliers,
    save_format: DataFormat = DataFormat.XLSX,
    data=Depends(get_user_data),
) -> FileResponse:
    result = await get_outliers(params=params, data=data)
    df = data["data"]
    if len(params.columns) != 0:
        df = df[params.columns]
    df = df.assign(**result)

    return TempStorage.return_file(df=df, save_format=save_format)


@router.post("/correlation")
async def get_correlation(
    params: DataForCorrelation,
    data=Depends(get_user_data),
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
    params: DataForCorrelation,
    save_format: DataFormat = DataFormat.XLSX,
    data=Depends(get_user_data),
) -> FileResponse:
    result = await get_correlation(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)
