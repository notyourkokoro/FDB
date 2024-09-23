import pandas as pd

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from starlette.background import BackgroundTask

from app.dependencies import get_user_data
from app.statistic.schemas import DataWithGroups
from app.statistic.builders import DataBuilder, DescriptiveStatisticsBuilder
from app.statistic.exceptions import ColumnsNotFoundException
from app.utils import TempStorage


router = APIRouter(prefix="/statistic", tags=["statistic"])


@router.post("/descriptive")
async def get_descriptive_statistics(
    params: DataWithGroups,
    data=Depends(get_user_data),
) -> dict:
    df = data["data"]

    columns = params.columns
    if columns:
        error_columns = set(columns) - set(df.columns)
        if len(error_columns) == 0:
            df = df[columns]
        else:
            raise ColumnsNotFoundException(columns=error_columns)

    datas = DataBuilder.build(df=df, groups=params.groups)

    return DescriptiveStatisticsBuilder.build(
        datas=datas, include_nan=params.include_nan
    )


@router.post("/descriptive/fast")
async def get_fast_descriptive_statistics(
    params: DataWithGroups,
    data=Depends(get_user_data),
) -> FileResponse:

    result = await get_descriptive_statistics(params=params, data=data)
    filename = TempStorage.create_file(pd.DataFrame(result))
    filepath = TempStorage.get_path(filename)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(TempStorage.delete_file, filepath=filepath),
    )
