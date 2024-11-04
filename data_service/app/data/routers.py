import pandas as pd
import numpy as np

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse

from app.dependencies import (
    get_current_user_token,
    get_user_data,
)
from app.memory import RedisConnection
from app.requests import get_user_uuid
from app.data.requests import StorageServiceRequests
from app.exceptions import ColumnsNotFoundException
from app.data.schemas import (
    MergeMethod,
    ParamsForMerge,
    ParamsForRecovery,
    ParamsForCalculate,
    ParamsForExpr,
    ParamsForSelect,
)
from app.data.builders import RecoveryDataBuilder
from app.utils import TempStorage
from app.validation import ValidateData
from app.data.exceptions import (
    ColumnsExistsException,
    EvalException,
    EvalTypeException,
    MergeColumnsTypeException,
)
from app.schemas import DataFormat

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/save")
async def save_df(
    data: dict = Depends(get_user_data),
    save_format: DataFormat = DataFormat.XLSX,
) -> FileResponse:
    return TempStorage.return_file(df=data["data"], save_format=save_format)


@router.get("/load/{file_id}")
async def load_file(
    file_id: int,
    sep: str | None = None,
    user_token: str = Depends(get_current_user_token),
):
    user_id = await get_user_uuid(user_token=user_token)
    df = await StorageServiceRequests.get_user_file(
        user_token=user_token, file_id=file_id, sep=sep
    )
    df = df.rename(columns={col: col.strip() for col in df.columns})

    await RedisConnection.set_dataframe(user_id=user_id, df=df, file_id=file_id)


@router.get("/columns")
async def get_columns(data: dict = Depends(get_user_data)) -> list[str]:
    return data["data"].columns.to_list()


@router.get("/info")
async def get_data_info(info: dict = Depends(get_user_data)) -> dict:
    return {
        "file_id": info["file_id"],
        "rows": len(info["data"]),
        "columns_count": len(info["data"].columns),
        "columns": info["data"].columns.to_list(),
    }


@router.get("/dataframe")
def get_dataframe(data: dict = Depends(get_user_data)) -> dict:
    return data["data"].to_dict()


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
    await RedisConnection.set_dataframe(user_id=user_id, df=df)

    return df.columns


@router.post("/store", status_code=status.HTTP_201_CREATED)
async def save_progress(
    save_format: DataFormat = DataFormat.XLSX,
    user_token: str = Depends(get_current_user_token),
    data: dict = Depends(get_user_data),
):
    file_id, df = data["file_id"], data["data"]

    filename = TempStorage.create_file(df=df, filetype=save_format)
    filepath = TempStorage.get_path(filename)

    try:
        with open(filepath, "rb") as buffer:
            response = await StorageServiceRequests.sent_file(
                user_token=user_token,
                file_id=file_id,
                file_obj=buffer,
                filetype=save_format,
            )
    except Exception as e:
        raise e
    finally:
        TempStorage.delete_file(filepath)

    await RedisConnection.set_file_id(user_id=data["user_id"], file_id=response["id"])


@router.patch("/recovery")
async def recovery_data(
    params: ParamsForRecovery, data: dict = Depends(get_user_data)
) -> dict:
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)
    recovery_df = RecoveryDataBuilder.recovery(
        df=df,
        method_name=str.lower(params.method.name),
        n_neighbors=params.n_neighbors,
    )

    if params.update_df is True:
        df = data["data"].assign(**recovery_df.to_dict())
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)
    return recovery_df.to_dict()


@router.post("/recovery/fast")
async def recovery_data_fast(
    params: ParamsForRecovery,
    save_format: DataFormat = DataFormat.XLSX,
    data: dict = Depends(get_user_data),
) -> FileResponse:
    result = await recovery_data(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.patch("/calculate")
async def calculate(
    params: ParamsForCalculate, data: dict = Depends(get_user_data)
) -> dict[str, list]:
    df = data["data"]

    if params.column_name in df.columns and params.rewrite is False:
        raise ColumnsExistsException([params.column_name])

    try:
        result = df.eval(params.expr)
    except pd.errors.UndefinedVariableError as error:
        raise ColumnsNotFoundException([error])
    except (ValueError, SyntaxError):
        raise EvalException
    except (TypeError, np._core._exceptions._UFuncNoLoopError):
        raise EvalTypeException
    if isinstance(result, pd.DataFrame):
        raise EvalException

    if params.convert_bool is True and isinstance(result.dtype, np.dtypes.BoolDType):
        result = result.astype(int)

    if params.update_df is True:
        df[params.column_name] = result
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return {params.column_name: result.to_list()}


@router.patch("/filter")
async def filter_data(
    params: ParamsForExpr, data: dict = Depends(get_user_data)
) -> dict:
    df = data["data"]

    try:
        filtered_df = df.query(params.expr)
    except pd.errors.UndefinedVariableError as error:
        raise ColumnsNotFoundException([error])
    except (ValueError, SyntaxError):
        raise EvalException
    except TypeError:
        raise EvalTypeException

    if params.update_df is True:
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=filtered_df)

    return filtered_df.to_dict()


@router.patch("/select")
async def select_data(
    params: ParamsForSelect, data: dict = Depends(get_user_data)
) -> dict:
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    if params.update_df is True:
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return df.to_dict()


@router.patch("/merge")
async def merge_data(
    params: ParamsForMerge,
    method: MergeMethod = MergeMethod.LEFT,
    data: dict = Depends(get_user_data),
    user_token: str = Depends(get_current_user_token),
) -> dict:
    ValidateData.check_columns(df=data["data"], columns=params.left_columns)

    df_for_merge = await StorageServiceRequests.get_user_file(
        user_token=user_token, file_id=params.other_file_id, sep=params.right_sep
    )
    ValidateData.check_columns(df=df_for_merge, columns=params.right_columns)

    try:
        result_df = pd.merge(
            data["data"],
            df_for_merge,
            how=method.value,
            left_on=params.left_columns,
            right_on=params.right_columns,
        )
    except ValueError:
        raise MergeColumnsTypeException

    if params.update_df is True:
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=result_df)

    return result_df.to_dict()
