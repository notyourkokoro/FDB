import pandas as pd
import numpy as np

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from starlette.background import BackgroundTask

from app.dependencies import (
    get_current_user_token,
    get_user_columns,
    get_user_data,
)
from app.memory import memory
from app.requests import get_user_file, get_user_uuid
from app.exceptions import ColumnsNotFoundException
from app.data.schemas import DataForRecovery, DataForCalculate
from app.data.builders import RecoveryDataBuilder
from app.utils import TempStorage, ValidateData
from app.data.exceptions import ColumnsExistsException, EvalException

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
        raise ColumnsNotFoundException(not_found_columns)

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


@router.post("/calculate")
async def calculate(
    params: DataForCalculate, data: dict = Depends(get_user_data)
) -> dict[str, list]:
    df = data["data"]

    if params.column_name in df.columns and params.rewrite is False:
        raise ColumnsExistsException([params.column_name])

    try:
        result = df.eval(params.expr)
    except pd.errors.UndefinedVariableError as error:
        raise ColumnsNotFoundException([error])
    except SyntaxError:
        raise EvalException

    if params.convert_bool is True and isinstance(result.dtype, np.dtypes.BoolDType):
        result = result.astype(int)

    if params.update_df:
        df[params.column_name] = result
        await memory.set_dataframe(user_id=data["user_id"], df=df)

    return {params.column_name: result.to_list()}
