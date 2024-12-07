from typing import Sequence

from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.storage import StogareController
from app.schemas import (
    AddGroupFile,
    AddUserFile,
    DeleteGroupFile,
    DeleteUserFile,
    StorageFileRead,
    StorageFileList,
    StorageFilePatch,
    AddUsersFile,
    StorageFileReadFull,
)
from app.repository import (
    add_file_for_group,
    create_user_file,
    remove_file,
    remove_file_from_group,
    remove_user_from_file,
    select_file,
    select_group,
    select_user_files,
    add_file_to_user,
    update_file,
    add_file_to_users,
)
from app.dependencies import get_current_user_uuid
from app.exceptions import (
    FileFormatException,
    FilePermissionException,
    BasedOnException,
    DeleteUserFileException,
    GroupPermissionException,
)
from app.permissions import StorageFilePermission
from app.models import FileTypeEnum

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_file(
    upload_file_obj: UploadFile = File(...),
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileRead:
    """
    Загрузка файла пользователем на сервер

    Parameters
    ----------
    upload_file_obj : UploadFile
        Файл, загружаемый пользователем
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFileRead
        Объект, представляющий информацию о загруженном файле
    """
    # Проверка формата файла
    if not upload_file_obj.filename.endswith(
        tuple(filetype.name for filetype in FileTypeEnum)
    ):
        raise FileFormatException

    # Получение пути для сохранения файла
    filepath = StogareController.get_filepath(
        filename=upload_file_obj.filename, user_id=user_id
    )
    # Создание файла на сервере (в хранилище)
    StogareController.create_file(filepath, upload_file_obj.file)

    # Создание записи о файле в базе данных
    created_file = await create_user_file(
        filename=upload_file_obj.filename,
        path=filepath,
        size=upload_file_obj.size,
        user_id=user_id,
        session=session,
    )

    return created_file


@router.post("/based/{file_id}", status_code=status.HTTP_201_CREATED)
async def based_on(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileReadFull:
    """
    Создание нового файла на основе существующего

    Parameters
    ----------
    file_id : int
        Идентификатор исходного файла
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFileReadFull
        Объект, представляющий информацию о созданном файле
    """
    # Проверка прав доступа пользователя к файлу
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException

    # Получение объекта пользовательского файла
    storage_file = data["storage_file"]

    # Проверка, что пользователь не может создать файл на основе своего
    if str(storage_file.creator_id) == user_id:
        raise BasedOnException

    # Получение пути для нового файла
    filepath = StogareController.get_filepath(
        filename=storage_file.filename, user_id=user_id
    )

    # Копирование содержимого исходного файла в новый файл
    StogareController.create_based_on(
        filepath_read=storage_file.path, filepath_output=filepath
    )
    # Создание записи о новом файле в базе данных
    created_file = await create_user_file(
        filename=storage_file.filename,
        path=filepath,
        size=storage_file.size,
        user_id=user_id,
        based_on_id=file_id,
        session=session,
    )

    return created_file


@router.post("/add/version", status_code=status.HTTP_201_CREATED)
async def add_version(
    based_file_id: int,
    upload_file_obj: UploadFile = File(...),
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileReadFull:
    """
    Добавление новой версии файла

    Parameters
    ----------
    based_file_id : int
        Идентификатор исходного файла
    upload_file_obj : UploadFile
        Новый файл, представляющий собой новую версию
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFileReadFull
        Объект, представляющий информацию о новой версии файла
    """
    # Проверка формата файла
    if not upload_file_obj.filename.endswith(
        tuple(filetype.name for filetype in FileTypeEnum)
    ):
        raise FileFormatException

    # Проверка прав доступа пользователя к файлу
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, based_file_id, session
    )

    if data["access"] is False:
        raise FilePermissionException

    # Получение объекта пользовательского файла
    storage_file = data["storage_file"]

    # Инкрементирование версии файла
    need_version = storage_file.version + 1

    # Формирование имени новой версии файла
    filename = StogareController.get_filename_based_on(
        filename_left=storage_file.filename,
        filename_right=upload_file_obj.filename,
    )
    # Формирование пути для новой версии файла
    filepath = StogareController.get_filepath(
        filename=filename,
        user_id=user_id,
        version=need_version,
    )

    # Создание файла для новой версии
    StogareController.create_file(filepath, upload_file_obj.file)
    # Добавление записи о новом файле в базу данных
    created_file = await create_user_file(
        filename=filename,
        path=filepath,
        size=upload_file_obj.size,
        user_id=user_id,
        based_on_id=based_file_id,
        version=need_version,
        session=session,
    )

    return created_file


@router.post("/add/user", status_code=status.HTTP_201_CREATED)
async def add_filelink_to_user(
    data_to_add: AddUserFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Добавление связи между файлом и пользователем

    Parameters
    ----------
    data_to_add : AddUserFile
        Данные, содержащие информацию о файле и пользователе,
        с котором нужно установить связь
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Добавление файла другому пользователю
    await add_file_to_user(
        user_id=user_id,
        to_user_id=data_to_add.to_user_id,
        file_id=data_to_add.file_id,
        session=session,
    )


@router.post("/add/users", status_code=status.HTTP_201_CREATED)
async def add_filelink_to_users(
    data_to_add: AddUsersFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Добавление связей с файлом нескольким пользователям

    Parameters
    ----------
    data_to_add : AddUsersFile
        Данные, содержащие информацию о файле и пользователях,
        с которыми нужно установить связь
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Добавление файла нескольким пользователям
    await add_file_to_users(
        user_id=user_id,
        to_user_ids=data_to_add.to_user_ids,
        file_id=data_to_add.file_id,
        session=session,
    )


@router.post("/add/group", status_code=status.HTTP_201_CREATED)
async def add_filelink_to_group(
    data_to_add: AddGroupFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Добавление связи между файлом и группой

    Parameters
    ----------
    data_to_add : AddGroupFile
        Данные, содержащие информацию о файле и группе,
        к которой нужно привязать файл
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Добавление файла в группу
    await add_file_for_group(
        user_id=user_id,
        group_id=data_to_add.group_id,
        file_id=data_to_add.file_id,
        session=session,
    )


@router.get("/list/my")
async def get_user_files(
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> Sequence[StorageFileList]:
    """
    Получение списка файлов текущего пользователя.
    ВАЖНО! Возвращает только связанные с пользователем файлы напрямую.
    Файлы в группах не учитываются

    Parameters
    ----------
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    Sequence[StorageFileList]
        Список файлов пользователя
    """
    return await select_user_files(user_id=user_id, session=session)


@router.get("/list/group/{group_id}")
async def get_group_files(
    group_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> Sequence[StorageFileList]:
    """
    Получение списка файлов пользовательской группы

    Parameters
    ----------
    group_id : int
        Идентификатор группы
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    Sequence[StorageFileList]
        Список файлов группы
    """
    # Получение объекта группы
    group = await select_group(group_id=group_id, session=session)

    # Проверка прав доступа пользователя к группе
    if user_id not in [str(user.id) for user in group.users]:
        raise GroupPermissionException

    return group.files


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileReadFull:
    """
    Получение подробной информации о конкретном файле

    Parameters
    ----------
    file_id : int
        Идентификатор файла
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFileReadFull
        Подробная информация о файле
    """
    # Проверка прав доступа пользователя к файлу
    # и получение объекта файла (при наличие прав доступа)
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException
    return data["storage_file"]


@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> FileResponse:
    """
    Скачивание файла

    Parameters
    ----------
    file_id : int
        Идентификатор файла
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    FileResponse
        Ответ с файлом для загрузки
    """
    # Получение файла (при наличие прав доступа)
    storage_file = await get_file(file_id=file_id, user_id=user_id, session=session)
    return FileResponse(storage_file.path, filename=storage_file.filename)


@router.patch("/rename/{file_id}")
async def patch_file(
    file_id: int,
    data_to_patch: StorageFilePatch,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> StorageFileReadFull:
    """
    Переименование файла

    Parameters
    ----------
    file_id : int
        Идентификатор файла
    data_to_patch : StorageFilePatch
        Данные для изменения имени файла
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Проверка прав доступа пользователя к файлу
    # и получение объекта файла (при наличие прав доступа)
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException

    # Получение объекта файла
    storage_file = data["storage_file"]
    # Получение типа файла
    filetype = FileTypeEnum(storage_file.type_id).name
    # Получение нового пути
    filepath = StogareController.get_filepath(
        filename="{name}.{type}".format(name=data_to_patch.filename, type=filetype),
        user_id=user_id,
    )

    # Переименование файла
    StogareController.rename_file(current_path=storage_file.path, new_path=filepath)

    # Обновление информации о файле в БД
    await update_file(
        storage_file=storage_file,
        data_to_update={"filename": data_to_patch.filename, "path": filepath},
        session=session,
    )

    return storage_file


@router.delete("/delete/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_from_file(
    params: DeleteUserFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Удаление доступа пользователя к файлу

    Parameters
    ----------
    data_to_delete : DeleteUserFile
        Данные для удаления доступа пользователя
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Проверка прав доступа пользователя к файлу
    # и получение объекта файла (при наличие прав доступа)
    storage_file = await select_file(file_id=params.file_id, session=session)
    if user_id not in [str(user.id) for user in storage_file.users]:
        raise FilePermissionException

    # Проверка на удаление связи с самим собой
    if params.to_user_id == storage_file.creator_id:
        raise DeleteUserFileException

    # Удаление связи между пользователем и файлом
    await remove_user_from_file(
        user_id=params.to_user_id, storage_file=storage_file, session=session
    )


@router.delete("/delete/group", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group_from_file(
    params: DeleteGroupFile,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Удаление связи между файлом и пользовательской группой

    Parameters
    ----------
    data_to_delete : DeleteGroupFile
        Данные для удаления файла из группы
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта группы
    group = await select_group(group_id=params.group_id, session=session)
    # Проверка прав доступа пользователя к группе
    if user_id not in [str(user.id) for user in group.users]:
        raise GroupPermissionException

    # Удаление связи между файлом и группой
    await remove_file_from_group(group=group, file_id=params.file_id, session=session)


@router.delete("/delete/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_file(
    file_id: int,
    user_id: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Удаление файла

    Parameters
    ----------
    file_id : int
        Идентификатор файла
    user_id : str
        Идентификатор текущего пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Проверка прав доступа пользователя к файлу
    # и получение объекта файла (при наличие прав доступа)
    data = await StorageFilePermission.check_user_access_with_data(
        user_id, file_id, session
    )
    if data["access"] is False:
        raise FilePermissionException
    storage_file = data["storage_file"]

    # Удаление файла на сервере (в хранилище)
    StogareController.delete_file(storage_file.path)
    # Удаление записи о файле из БД
    await remove_file(storage_file=storage_file, session=session)
