import pandas as pd

from fastapi import APIRouter, Depends
from starlette.background import BackgroundTask

from app.dependencies import (
    get_current_user_token,
    get_user_columns,
    get_user_data,
)
from app.memory import memory
from app.requests import get_user_file, get_user_uuid
from app.data.exceptions import ColumnsNotFound
from app.data.schemas import DataForRecovery
from app.data.builders import RecoveryDataBuilder
from app.utils import TempStorage, ValidateData
from fastapi.responses import FileResponse

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/load/{file_id}")
async def load_file(file_id: int, user_token: str = Depends(get_current_user_token)):
    file_obj = await get_user_file(user_token=user_token, file_id=file_id)
    user_id = await get_user_uuid(user_token=user_token)

    df = pd.read_excel(file_obj)
    df = df.rename(columns={col: col.strip() for col in df.columns})

    await memory.set_dataframe(user_id=user_id, df=df)


@router.get("/columns")
async def get_columns(columns: list = Depends(get_user_columns)) -> list[str]:
    return columns


@router.patch("/columns/rename")
async def rename_columns(
    columns: dict[str, str], data: dict = Depends(get_user_data)
) -> list[str]:
    df, user_id = data["data"], data["user_id"]

    not_found_columns = []
    for column in columns.keys():
        if column not in df.columns:
            not_found_columns.append(column)

    if len(not_found_columns) != 0:
        raise ColumnsNotFound(not_found_columns)

    df.rename(columns=columns, inplace=True)
    await memory.set_dataframe(user_id=user_id, df=df)

    return df.columns


@router.post("/recovery")
async def recovery_data(
    params: DataForRecovery, data: dict = Depends(get_user_data)
) -> dict:
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    recovery_df = RecoveryDataBuilder.recovery(
        df=df,
        method_name=str.lower(params.method.name),
        n_neighbors=params.n_neighbors,
    )
    return recovery_df.to_dict()


@router.post("/recovery/fast")
async def recovery_data_fast(
    params: DataForRecovery, data: dict = Depends(get_user_data)
) -> FileResponse:
    result = await recovery_data(params=params, data=data)

    filename = TempStorage.create_file(pd.DataFrame(result))
    filepath = TempStorage.get_path(filename)

    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(TempStorage.delete_file, filepath=filepath),
    )
