import pandas as pd

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user_token, get_user_columns
from app.memory import memory
from app.requests import get_user_file, get_user_uuid

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/load/{file_id}")
async def load_file(file_id: int, user_token: str = Depends(get_current_user_token)):
    file_obj = await get_user_file(user_token=user_token, file_id=file_id)
    user_id = await get_user_uuid(user_token=user_token)

    df = pd.read_excel(file_obj)

    await memory.set_dataframe(user_id=user_id, df=df)


@router.get("/columns")
async def get_columns(columns: list = Depends(get_user_columns)):
    return columns
