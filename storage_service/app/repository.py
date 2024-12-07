from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Group, StorageFile, User
from app.storage import StogareController
from app.exceptions import (
    FileGroupExistsException,
    FilePermissionException,
    FileNotFoundException,
    UserNotFoundException,
    FileExistsException,
    UsersNotFoundException,
    UserAccessToStorageFile,
    GroupNotFoundException,
    GroupPermissionException,
    FileInGroupNotFoundException,
)


async def select_user(user_id: str, session: AsyncSession) -> User:
    """
    Получение пользователя по его идентификатору

    Parameters
    ----------
    user_id : str
        Идентификатор пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    User
        Возвращает объект пользователя
    """
    # Запрос для получения пользователя с загрузкой объектов файлов, присоединенных к пользователю
    stmt = select(User).options(selectinload(User.files)).where(User.id == user_id)
    # Выполнение запроса
    user = await session.scalar(stmt)
    if user is None:
        raise UserNotFoundException
    return user


async def select_users(session: AsyncSession, user_ids: list[str]) -> list[User]:
    """
    Получение списка пользователей по их идентификаторам

    Parameters
    ----------
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    user_ids : list[str]
        Список идентификаторов пользователей

    Returns
    -------
    list[User]
        Список объектов пользователей
    """
    # Запрос для получения списка пользователей
    stmt = select(User).where(User.id.in_(user_ids))
    # Выполнение запроса
    users = list(await session.scalars(stmt))

    # Проверка наличия объектов пользователей для всех идентификаторов
    if len(user_ids) != len(users):
        current_user_ids = [user.id for user in users]
        # Если нет некоторых (хотя бы один) пользователей, рейсится исключение
        raise UsersNotFoundException(
            user_ids=list(filter(lambda x: x not in current_user_ids, user_ids))
        )

    return users


async def select_file(file_id: int, session: AsyncSession) -> StorageFile:
    """
    Получение файла по его идентификатору

    Parameters
    ----------
    file_id : int
        Идентификатор файла
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFile
        Объект файла
    """
    # Запрос для получения файла с загрузкой
    # объектов пользователей,присоединенных к файлу
    stmt = (
        select(StorageFile)
        .options(selectinload(StorageFile.users))
        .where(StorageFile.id == file_id)
    )

    # Выполнение запроса
    storage_file = await session.scalar(stmt)
    # Проверка объекта файла на наличие
    if storage_file is None:
        raise FileNotFoundException
    return storage_file


async def select_group(group_id: int, session: AsyncSession) -> Group:
    """
    Получение пользовательской группы по её идентификатору

    Parameters
    ----------
    group_id : int
        Идентификатор группы
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    Group
        Объект группы
    """
    # Запрос для получения группы с загрузкой объектов пользователей,
    # присоединенных к группе, и объектов файлов, привязанных к группе
    stmt = (
        select(Group)
        .options(selectinload(Group.users))
        .options(selectinload(Group.files))
        .where(Group.id == group_id)
    )

    # Выполнение запроса
    group = await session.scalar(stmt)
    # Проверка объекта группы на наличие
    if group is None:
        raise GroupNotFoundException
    return group


async def create_user_file(
    filename: str,
    path: str,
    size: int,
    user_id: str,
    session: AsyncSession,
    version: int = 1,
    based_on_id: int | None = None,
) -> StorageFile:
    """
    Создание нового файла пользователя

    Parameters
    ----------
    filename : str
        Имя файла
    path : str
        Путь к файлу
    size : int
        Размер файла
    user_id : str
        Идентификатор пользователя, создающего файл
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    version : int, optional
        Версия файла, по умолчанию 1
    based_on_id : int | None, optional
        Идентификатор файла, на основе которого создается новый файл, по умолчанию None

    Returns
    -------
    StorageFile
        Созданный файл
    """
    # Создание нового объекта пользовательского файла
    created_file: StorageFile = StorageFile(
        creator_id=user_id,
        filename=filename,
        path=path,
        size=size,
        type_id=StogareController.get_filetype_id(filename),
        version=version,
        based_on_id=based_on_id,
    )

    # Добавление нового объекта пользовательского файла в базу данных
    session.add(created_file)

    # Добавление связи между новым объектом файла и пользователем
    user = await select_user(user_id=user_id, session=session)
    user.files.append(created_file)

    # Сохранение изменений
    await session.commit()

    return created_file


async def select_user_files(
    user_id: str, session: AsyncSession
) -> Sequence[StorageFile]:
    """
    Получение всех файлов пользователя

    Parameters
    ----------
    user_id : str
        Идентификатор пользователя
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    Sequence[StorageFile]
        Список файлов пользователя
    """
    # Получение объекта пользователя
    user = await select_user(user_id=user_id, session=session)
    return user.files


async def add_file_to_user(
    user_id: str, to_user_id: str, file_id: int, session: AsyncSession
):
    """
    Добавление связи между файлом и пользователем

    Parameters
    ----------
    user_id : str
        Идентификатор пользователя, создавшего файл
    to_user_id : str
        Идентификатор пользователя, которому добавляется файл
    file_id : int
        Идентификатор файла
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта файла
    storage_file = await select_file(file_id=file_id, session=session)

    # Проверка, является ли пользователь создателем файла
    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    # Получение объекта пользователя, которому добавляется файл
    user = await select_user(user_id=to_user_id, session=session)

    # Проверка на наличие файла в списке файлов
    # пользователя,которому добавляется файл
    if storage_file in user.files:
        raise FileExistsException([to_user_id])

    # Добавление связи между файлом и пользователем
    user.files.append(storage_file)
    # Сохранение изменений
    await session.commit()


async def add_file_to_users(
    user_id: str, to_user_ids: list[str], file_id: int, session: AsyncSession
):
    """
    Добавление файла нескольким пользователям

    Parameters
    ----------
    user_id : str
        Идентификатор пользователя, создавшего файл
    to_user_ids : list[str]
        Список идентификаторов пользователей, которым добавляется файл
    file_id : int
        Идентификатор файла
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта файла
    storage_file = await select_file(file_id=file_id, session=session)

    # Проверка, является ли пользователь создателем файла
    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    # Получение списка объектов пользователей, которым нужно добавить файл
    users = await select_users(session=session, user_ids=to_user_ids)

    # Проверка на наличие файла у пользователей, которым нужно добавить файл
    users_with_file = []
    for user in users:
        if user in storage_file.users:
            users_with_file.append(user.id)

    # Если хотя бы один пользователь уже
    # имеет файл,рейсится исключение
    if len(users_with_file) != 0:
        raise FileExistsException(users_with_file)

    # Добавление связи между файлом и пользователями
    storage_file.users.extend(list(users))
    # Сохранение изменений
    await session.commit()


async def update_file(
    storage_file: StorageFile, data_to_update: dict, session: AsyncSession
) -> StorageFile:
    """
    Обновление данных файла

    Parameters
    ----------
    storage_file : StorageFile
        Файл, данные которого необходимо обновить
    data_to_update : dict
        Словарь с новыми значениями
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных

    Returns
    -------
    StorageFile
        Обновленный файл
    """
    # Запрос на обновление записи в БД о файле
    stmt = (
        update(StorageFile)
        .where(
            (StorageFile.creator_id == storage_file.creator_id)
            & (StorageFile.filename == storage_file.filename)
        )
        .values(**data_to_update)
    )

    # Выполнение запроса и сохранение изменений
    await session.execute(stmt)
    await session.commit()
    await session.refresh(storage_file)

    return storage_file


async def remove_file(storage_file: StorageFile, session: AsyncSession):
    """
    Удаление файла

    Parameters
    ----------
    storage_file : StorageFile
        Файл, который нужно удалить
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Удаление файла и сохранение изменений
    await session.delete(storage_file)
    await session.commit()


async def remove_user_from_file(
    storage_file: StorageFile, user_id: str, session: AsyncSession
):
    """
    Удаление пользователя из файла

    Parameters
    ----------
    storage_file : StorageFile
        Файл, из которого нужно удалить пользователя
    user_id : str
        Идентификатор пользователя, которого нужно удалить
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта пользователя
    user = await select_user(user_id=user_id, session=session)
    # Рейсление исключения, если пользователь не имеет доступа к файлу
    if user not in storage_file.users:
        raise UserAccessToStorageFile

    # Удаление пользователя из пользователей, привязанных к файлу
    storage_file.users.remove(user)
    # Сохранение изменений
    await session.commit()


async def add_file_for_group(
    user_id: str, group_id: str, file_id: int, session: AsyncSession
):
    """
    Добавление файла в группу

    Parameters
    ----------
    user_id : str
        Идентификатор пользователя, создавшего файл
    group_id : str
        Идентификатор группы, в которую нужно добавить файл
    file_id : int
        Идентификатор файла
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта пользовательского файла
    storage_file = await select_file(file_id=file_id, session=session)

    # Проверка, является ли пользователь создателем файла
    if user_id != str(storage_file.creator_id):
        raise FilePermissionException

    # Получение объекта группы
    group = await select_group(group_id=group_id, session=session)

    # Рейсление исключения, если пользователь не имеет доступа к группе
    if user_id not in [str(user.id) for user in group.users]:
        raise GroupPermissionException

    # Проверка на наличие файла в списке файлов группы.
    # Рейсление исключения, если файл уже привязан к группе
    if storage_file in group.files:
        raise FileGroupExistsException(name=group.name)

    # Добавление файла в список файлов группы и сохранение изменений
    group.files.append(storage_file)
    await session.commit()


async def remove_file_from_group(group: Group, file_id: int, session: AsyncSession):
    """
    Удаление файла из группы

    Parameters
    ----------
    group : Group
        Группа, из которой нужно удалить файл
    file_id : int
        Идентификатор файла
    session : AsyncSession
        Ассинхронная сессия для выполнения запросов к базе данных
    """
    # Получение объекта файла
    storage_file = await select_file(file_id=file_id, session=session)
    # Рейсление исключения, если файл не привязан к группе
    if storage_file not in group.files:
        raise FileInGroupNotFoundException

    # Удаление файла из списка файлов группы и сохранение изменений
    group.files.remove(storage_file)
    await session.commit()
