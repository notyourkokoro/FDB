from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse
import matplotlib.pyplot as plt
import seaborn as sns

from app.schemas import (
    CorrelationMethod,
    DataForVisualizationCorrelation,
    DataForVisualizationCorrelationFast,
    ImageFormat,
)
from app.validation import CorrelationValidation
from app.dependencies import get_user_data
from app.utils import TempStorage
from app.builders import CorrelationBuilder

router = APIRouter(prefix="/visualization", tags=["visualization"])


@router.post("/correlation")
async def get_correlation(
    params: DataForVisualizationCorrelation,
    method: CorrelationMethod = CorrelationMethod.SPEARMAN,
    data=Depends(get_user_data),
) -> dict[str, dict[str, float | None]]:
    df = CorrelationValidation.validate(df=data["data"], columns=params.columns)

    result = CorrelationBuilder.build(
        df=df, method=method, round_value=params.round_value, replace_nan=True
    )

    return result.to_dict()


@router.post("/correlation/fast")
async def get_correlation_fast(
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
