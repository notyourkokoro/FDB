from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import seaborn as sns

from app.schemas import (
    CorrelationMethod,
    DataForScatterplot,
    DataForScatterplotFast,
    DataForVisualizationCorrelation,
    DataForVisualizationCorrelationFast,
    ImageFormat,
)
from app.validation import CorrelationValidation, ValidateData
from app.dependencies import get_user_data
from app.utils import TempStorage
from app.builders import CorrelationBuilder

router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.post("/heatmap")
async def get_heatmap(
    params: DataForVisualizationCorrelation,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    data=Depends(get_user_data),
) -> dict[str, dict[str, float | None]]:
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    result = CorrelationBuilder.build(
        df=df, method=method, round_value=params.round_value, replace_nan=True
    )

    return result.to_dict()


@router.post("/heatmap/fast")
async def get_heatmap_fast(
    params: DataForVisualizationCorrelationFast,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    save_format: ImageFormat = ImageFormat.PNG,
    data=Depends(get_user_data),
) -> FileResponse:
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    result = CorrelationBuilder.build(df=df, method=method)

    fig_width = result.shape[1]  # ширина зависит от количества столбцов
    fig_height = result.shape[0]  # высота зависит от количества строк

    plt.figure(figsize=(fig_width, fig_height))
    sns.heatmap(
        result,
        annot=True,
        cmap="YlGnBu",
        cbar=params.cbar,
        xticklabels=result.columns,
        yticklabels=result.index,
    )

    plt.xticks(rotation=params.x_lable_rotation)

    if params.title is not None:
        plt.title(params.title)

    return TempStorage.return_file(save_format=save_format)


@router.post("/scatterplot")
async def get_scatterplot(
    params: DataForScatterplot,
    data=Depends(get_user_data),
) -> dict:
    columns = [params.x_column, params.y_column]
    if params.hue_column is not None:
        columns.append(params.hue_column)

    df = ValidateData.check_columns(df=data["data"], columns=columns)

    return df.to_dict()


@router.post("/scatterplot/fast")
async def get_scatterplot_fast(
    params: DataForScatterplotFast,
    save_format: ImageFormat = ImageFormat.PNG,
    data=Depends(get_user_data),
) -> dict:
    columns = [params.x_column, params.y_column]
    if params.hue_column is not None:
        columns.append(params.hue_column)

    df = ValidateData.check_columns(df=data["data"], columns=columns)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x=params.x_column,
        y=params.y_column,
        hue=params.hue_column,
        palette="viridis",
        s=params.dot_size,
        legend="auto" if params.need_legend is True else False,
    )

    plt.xlabel(params.x_column)
    plt.ylabel(params.y_column)

    if params.title is not None:
        plt.title(params.title)

    return TempStorage.return_file(save_format=save_format)
