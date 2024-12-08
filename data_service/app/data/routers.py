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

# Создание роутера для маршрутов для работы с данными
router = APIRouter(prefix="/data", tags=["data"])


@router.get("/save")
async def save_df(
    data: dict = Depends(get_user_data),
    save_format: DataFormat = DataFormat.XLSX,
) -> FileResponse:
    """
    Сохранение DataFrame из Redis в файл

    Parameters
    ----------
    data : dict
        Данные текущего пользователя в Redis
    save_format : DataFormat
        Формат файла для сохранения (например, XLSX)

    Returns
    -------
    FileResponse
        Ответ с файлом в указанном формате
    """
    return TempStorage.return_file(df=data["data"], save_format=save_format)


@router.get("/load/{file_id}")
async def load_file(
    file_id: int,
    sep: str | None = None,
    user_token: str = Depends(get_current_user_token),
):
    """
    Загрузка данных из файла в Redis

    Parameters
    ----------
    file_id : int
        Идентификатор файла, который нужно загрузить
    sep : str, optional
        Разделитель для CSV файла (если не указан, выбрасывает исключение)
    user_token : str
        Токен текущего пользователя
    """
    # Получаем UUID пользователя
    user_id = await get_user_uuid(user_token=user_token)

    # Получение файла из сервиса для хранения пользовательских
    # файлов,чтение в pandas DataFrame
    df = await StorageServiceRequests.get_user_file(
        user_token=user_token, file_id=file_id, sep=sep
    )

    # Удаление пробельных символов в названиях колонок
    df = df.rename(columns={col: col.strip() for col in df.columns})

    # Сохраняем данные в Redis
    await RedisConnection.set_dataframe(user_id=user_id, df=df, file_id=file_id)


@router.get("/columns")
async def get_columns(data: dict = Depends(get_user_data)) -> list[str]:
    """
    Получение списка колонок данных

    Parameters
    ----------
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    list[str]
        Список названий колонок в DataFrame
    """
    return data["data"].columns.to_list()


@router.get("/info")
async def get_data_info(info: dict = Depends(get_user_data)) -> dict:
    """
    Получение информации о загруженных
    пользователем ранее данных в DataFrame

    Parameters
    ----------
    info : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Словарь с информацией о данных
        (количество строк, количество колонок, их названия)
    """
    return {
        "file_id": info["file_id"],
        "rows": len(info["data"]),
        "columns_count": len(info["data"].columns),
        "columns": info["data"].columns.to_list(),
    }


@router.get("/dataframe")
def get_dataframe(data: dict = Depends(get_user_data)) -> dict:
    """
    Получение DataFrame в виде словаря

    Parameters
    ----------
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        DataFrame в виде словаря
    """
    return data["data"].to_dict()


@router.patch("/columns/rename")
async def rename_columns(
    columns: dict[str, str], data: dict = Depends(get_user_data)
) -> list[str]:
    """
    Переименование колонок в DataFrame

    Parameters
    ----------
    columns : dict[str, str]
        Словарь, где ключ - старое название
        колонки, а значение - новое название
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    list[str]
        Список всех колонок после переименования
    """
    # Получение DataFrame и идентификатора пользователя
    df, user_id = data["data"], data["user_id"]

    # Проверка наличия указанных колонок в DataFrame
    not_found_columns = []
    for column in columns.keys():
        if column not in df.columns:
            not_found_columns.append(column)

    # Рейсится исключения для колонок, которые не были наидены
    if len(not_found_columns) != 0:
        raise ColumnsNotFoundException(not_found_columns)

    # Переименование колонок
    df.rename(columns=columns, inplace=True)

    # Сохраняем обновленные данные в Redis
    await RedisConnection.set_dataframe(user_id=user_id, df=df)

    return df.columns


@router.post("/store", status_code=status.HTTP_201_CREATED)
async def save_progress(
    save_format: DataFormat = DataFormat.XLSX,
    user_token: str = Depends(get_current_user_token),
    data: dict = Depends(get_user_data),
):
    """
    Сохранение данных в сервисе для
    хранения пользовательских файлов

    Parameters
    ----------
    save_format : DataFormat
        Формат файла для сохранения
    user_token : str
        Токен текущего пользователя
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Информация о загруженном файле
    """
    # Получение DataFrame и идентификатора файла,
    # на основе которого был получен DataFrame
    file_id, df = data["file_id"], data["data"]

    # Создание ими файла на основе полученного формата
    filename = TempStorage.create_file(df=df, filetype=save_format)
    filepath = TempStorage.get_path(filename)

    try:
        # Отправляем файл в сервис для хранения файлов
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
        # Удаление временного файла
        TempStorage.delete_file(filepath)

    # Сохранение нового ID файла в Redis
    await RedisConnection.set_file_id(user_id=data["user_id"], file_id=response["id"])


@router.patch("/recovery")
async def recovery_data(
    params: ParamsForRecovery, data: dict = Depends(get_user_data)
) -> dict:
    """
    Восстановление данных

    Parameters
    ----------
    params : ParamsForRecovery
        Параметры для восстановления данных
        (метод, количество соседей для KNN)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Восстановленные данные в виде словаря
    """
    # Проверка наличия указанных колонок
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    # Восстановление данных с использованием указанного метода
    recovery_df = RecoveryDataBuilder.recovery(
        df=df,
        method_name=str.lower(params.method.name),
        n_neighbors=params.n_neighbors,
    )

    # Обновление данные в Redis, если требуется
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
    """
    Восстановление данных с последующим
    получением файла пользователем

    Parameters
    ----------
    params : ParamsForRecovery
        Параметры для восстановления данных
    save_format : DataFormat
        Формат файла для сохранения
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    FileResponse
        Ответ с файлом, содержащим восстановленные данные
    """
    result = await recovery_data(params=params, data=data)
    return TempStorage.return_file(df=pd.DataFrame(result), save_format=save_format)


@router.patch("/calculate")
async def calculate(
    params: ParamsForCalculate, data: dict = Depends(get_user_data)
) -> dict[str, list]:
    """
    Добавление вычисляемой колонки в DataFrame

    Parameters
    ----------
    params : ParamsForCalculate
        Параметры для вычислений (выражение, название столбца)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict[str, list]
        Результат вычислений в виде словаря
    """
    # Получение DataFrame текущего пользователя
    df = data["data"]

    # Проверка на существование столбца с таким же названием
    if params.column_name in df.columns and params.rewrite is False:
        raise ColumnsExistsException([params.column_name])

    try:
        # Выполнение вычислений с использованием выражения
        result = df.eval(params.expr)
    except pd.errors.UndefinedVariableError as error:
        raise ColumnsNotFoundException([error])
    except (ValueError, SyntaxError):
        raise EvalException
    except (TypeError, np._core._exceptions._UFuncNoLoopError):
        raise EvalTypeException

    if isinstance(result, pd.DataFrame):
        raise EvalException

    # Преобразование типа данных из bool в int, если требуется
    # (допустим, пользователь хочет поделить данные на группы)
    if params.convert_bool is True and isinstance(result.dtype, np.dtypes.BoolDType):
        result = result.astype(int)

    # Обновление данных в Redis, если требуется
    if params.update_df is True:
        df[params.column_name] = result
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=df)

    return {params.column_name: result.to_list()}


@router.patch("/filter")
async def filter_data(
    params: ParamsForExpr, data: dict = Depends(get_user_data)
) -> dict:
    """
    Применение фильтрации к данным

    Parameters
    ----------
    params : ParamsForExpr
        Параметры для фильтрации
        (выражение для фильтрации)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Отфильтрованные данные в виде словаря
    """
    # Получаем DataFrame текущего пользователя
    df = data["data"]

    try:
        # Попытка применить фильтрацию к данным
        filtered_df = df.query(params.expr)
    except pd.errors.UndefinedVariableError as error:
        raise ColumnsNotFoundException([error])
    except (ValueError, SyntaxError):
        raise EvalException
    except TypeError:
        raise EvalTypeException

    # Обновление данных в Redis, если требуется
    if params.update_df is True:
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=filtered_df)

    return filtered_df.to_dict()


@router.patch("/select")
async def select_data(
    params: ParamsForSelect, data: dict = Depends(get_user_data)
) -> dict:
    """
    Усечение DataFrame по столбцам

    Parameters
    ----------
    params : ParamsForSelect
        Параметры для усечения данных по столбцам
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        DataFrame с выбранными столбцами в виде словаря
    """
    # Получение DataFrame текущего пользователя и проверка наличия указанных столбцов
    df = ValidateData.check_columns(df=data["data"], columns=params.columns)

    # Обновление данных в Redis, если требуется
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
    """
    Объединение данных с другим файлом

    Parameters
    ----------
    params : ParamsForMerge
        Параметры для объединения данных
    method : MergeMethod
        Метод объединения (left, right, inner, outer, cross, merge)
    data : dict
        Данные текущего пользователя в Redis

    Returns
    -------
    dict
        Результат объединения данных в виде словаря
    """
    # Проверка наличия указанных колонок в текущем DataFrame пользователя
    ValidateData.check_columns(df=data["data"], columns=params.left_columns)

    # Получение DataFrame для объединения из сервиса для хранения файлов
    df_for_merge = await StorageServiceRequests.get_user_file(
        user_token=user_token, file_id=params.other_file_id, sep=params.right_sep
    )
    # Проверка наличия указанных колонок в DataFrame для объединения
    ValidateData.check_columns(df=df_for_merge, columns=params.right_columns)

    try:
        # Попытка объединить данные
        result_df = pd.merge(
            data["data"],
            df_for_merge,
            how=method.value,
            left_on=params.left_columns,
            right_on=params.right_columns,
        )
    except ValueError:
        raise MergeColumnsTypeException

    # Обновление текущих данных в Redis, если требуется
    if params.update_df is True:
        await RedisConnection.set_dataframe(user_id=data["user_id"], df=result_df)

    return result_df.to_dict()
