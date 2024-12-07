from typing import Sequence
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.auth.models import User
from app.group.models import Group
from app.group.exceptions import (
    UserNotFoundException,
    UsersNotFoundException,
    GroupNotFoundException,
    GroupPermissionException,
    GroupExistsException,
    UsersInGroupExistsException,
    ContaionsUserInGroupException,
)


async def select_user(user_id: UUID, session: AsyncSession) -> User:
    """
    Получает пользователя по идентификатору с загрузкой групп

    Parameters
    ----------
    user_id : UUID
        Идентификатор пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    User
        Объект пользователя

    Raises
    ------
    UserNotFoundException
        Исключение, если пользователь не найден
    """
    # Запрос для получения пользователя вместе с загрузкой групп
    stmt = select(User).options(selectinload(User.groups)).where(User.id == user_id)
    # Выполнение запроса
    user = await session.scalar(stmt)
    # Проверка пользователя на существование
    if user is None:
        raise UserNotFoundException
    return user


async def select_users(session: AsyncSession, user_ids: list[UUID]) -> list[User]:
    """
    Получает список пользователей по идентификаторам

    Parameters
    ----------
    session : AsyncSession
        Асинхронная сессия базы данных
    user_ids : list[UUID]
        Список идентификаторов пользователей

    Returns
    -------
    list[User]
        Список объектов пользователей

    Raises
    ------
    UsersNotFoundException
        Исключение, если некоторые (хотя бы один) пользователи не найдены
    """
    # Запрос для получения списка пользователей
    stmt = select(User).where(User.id.in_(user_ids))
    # Выполнение запроса
    users = list(await session.scalars(stmt))

    # Проверка наличия объектов пользователей для всех идентификаторов
    if len(user_ids) != len(users):
        current_user_ids = [user.id for user in users]
        raise UsersNotFoundException(
            user_ids=list(filter(lambda x: x not in current_user_ids, user_ids))
        )

    return users


async def create_group(name: str, user_id: UUID, session: AsyncSession) -> Group:
    """
    Создает группу с указанным именем и добавлением ее создателя

    Parameters
    ----------
    name : str
        Имя группы
    user_id : UUID
        Идентификатор создателя группы
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    Group
        Объект созданной группы

    Raises
    ------
    GroupExistsException
        Исключение, если группа с таким именем уже существует
    """
    try:
        # Создание объекта группы
        created_group = Group(creator_id=user_id, name=name)

        # Добавление группы в сессию
        session.add(created_group)

        # Получение объекта пользователя
        user = await select_user(user_id=user_id, session=session)
        # Добавление создателя группы в группу
        user.groups.append(created_group)

        # Сохранение изменений
        await session.commit()

        return created_group
    except IntegrityError:
        raise GroupExistsException


async def select_group(group_id: int, session: AsyncSession) -> Group:
    """
    Получает группу по идентификатору с загрузкой пользователей

    Parameters
    ----------
    group_id : int
        Идентификатор группы
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    Group
        Объект группы

    Raises
    ------
    GroupNotFoundException
        Рейсит исключение, если группа не найдена
    """
    # Запрос для получения группы вместе с загрузкой пользователей
    stmt = select(Group).options(selectinload(Group.users)).where(Group.id == group_id)
    # Выполнение запроса
    group = await session.scalar(stmt)
    if group is None:
        raise GroupNotFoundException
    return group


async def select_user_groups(user_id: UUID, session: AsyncSession) -> Sequence[Group]:
    """
    Получает список групп, в которых состоит пользователь

    Parameters
    ----------
    user_id : UUID
        Идентификатор пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    Sequence[Group]
        Список обектов-групп
    """
    # Получение объекта пользователя вместе с загрузкой групп
    user = await select_user(user_id=user_id, session=session)
    return user.groups


async def add_users_to_group(
    user_id: UUID, to_user_ids: list[UUID], group_id: int, session: AsyncSession
):
    """
    Добавляет пользователей в группу

    Parameters
    ----------
    user_id : UUID
        Идентификатор текущего пользователя
    to_user_ids : list[UUID]
        Список идентификаторов добавляемых пользователей
    group_id : int
        Идентификатор группы
    session : AsyncSession
        Асинхронная сессия базы данных

    Raises
    ------
    GroupPermissionException
        Рейсится, если текущий пользователь не состоит в группе
    UsersInGroupExistsException
        Рейсится, если некоторые (хотя бы один) пользователи уже состоят в группе
    """
    # Получение объекта группы
    group = await select_group(group_id=group_id, session=session)

    # Проверка пользователя, который добавляет других, на наличие в группе
    if user_id not in [user.id for user in group.users]:
        raise GroupPermissionException

    # Получение объектов пользователей, которых нужно добавить в группу
    users = await select_users(session=session, user_ids=to_user_ids)

    # Проверка на наличие пользователей, которых надо добавить, в группе
    users_with_group = []
    for user in users:
        if user in group.users:
            users_with_group.append(user.id)

    if len(users_with_group) != 0:
        raise UsersInGroupExistsException(users_with_group)

    # Добавление пользователей в группу
    group.users.extend(list(users))
    await session.commit()


async def update_group(group: Group, name: str, session: AsyncSession) -> Group:
    """
    Обновляет информацию о группе

    Parameters
    ----------
    group : Group
        Объект группы
    name : str
        Новое имя группы
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    Group
        Обновленный объект группы

    Raises
    ------
    GroupExistsException
        Рейсится, если группа с таким именем уже существует
    """
    try:
        # Запрос для обновления имени группы по текущему имени
        stmt = update(Group).where(Group.name == group.name).values(name=name)

        # Выплнение запроса
        await session.execute(stmt)
        await session.commit()
        await session.refresh(group)

        return group
    except IntegrityError:
        raise GroupExistsException


async def remove_group(group: Group, session: AsyncSession):
    """
    Удаляет группу

    Parameters
    ----------
    group : Group
        Объект группы
    session : AsyncSession
        Асинхронная сессия базы данных
    """
    await session.delete(group)
    await session.commit()


async def remove_user_from_group(group: Group, user_id: UUID, session: AsyncSession):
    """
    Удаляет пользователя из группы

    Parameters
    ----------
    group : Group
        Объект группы
    user_id : UUID
        Идентификатор пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Raises
    ------
    ContaionsUserInGroupException
        Рейсится, если пользователь не состоит в группе
    """
    # Получение объекта пользователя
    user = await select_user(user_id=user_id, session=session)
    # Проверка пользователя на наличие в группе
    if user not in group.users:
        raise ContaionsUserInGroupException

    # Удаление пользователя из группы
    group.users.remove(user)
    await session.commit()
