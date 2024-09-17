import pandas as pd

from fastapi import APIRouter, Depends

from app.dependencies import (
    get_current_user_token,
    get_user_columns,
    get_user_data,
)
from app.memory import memory
from app.requests import get_user_file, get_user_uuid
from app.data.exceptions import ColumnsNotFound

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/load/{file_id}")
async def load_file(file_id: int, user_token: str = Depends(get_current_user_token)):
    file_obj = await get_user_file(user_token=user_token, file_id=file_id)
    user_id = await get_user_uuid(user_token=user_token)

    df = pd.read_excel(file_obj)

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
