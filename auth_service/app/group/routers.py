from typing import Sequence
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_db
from app.auth.models import User
from app.auth.manager import current_user
from app.group.schemas import (
    GroupCreate,
    GroupRead,
    ParamsAddUserToGroup,
    ParamsAddUsersToGroup,
    GroupUpdate,
    ParamsDeleteUserFromGroup,
)
from app.group.repository import (
    create_group,
    remove_group,
    select_group,
    select_user_groups,
    add_users_to_group,
    update_group,
    remove_user_from_group,
)
from app.group.exceptions import GroupPermissionException, DeleteUserFromGroupException

# Создание маршрутизатора для работы с группами
router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("/list/my")
async def get_groups(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> Sequence[GroupRead]:
    """
    Получить список групп, в которых состоит Объект текущего пользователя

    Parameters
    ----------
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    Sequence[GroupRead]
        Список групп пользователя
    """
    groups = await select_user_groups(user_id=user.id, session=session)
    return groups


@router.get("/{group_id}")
async def get_group(
    group_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> GroupRead:
    """
    Получить информацию о пользовательскойгруппе по идентификатору

    Parameters
    ----------
    group_id : int
        Идентификатор группы
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    GroupRead
        Информация о группе
    """
    group = await select_group(group_id=group_id, session=session)
    return group


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user_group(
    params: GroupCreate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> GroupRead:
    """
    Создать новую пользовательскую группу

    Parameters
    ----------
    params : GroupCreate
        Параметры для создания группы
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    GroupRead
        Информация о созданной группе
    """
    group = await create_group(name=params.name, user_id=user.id, session=session)
    return group


@router.post("/add/user", status_code=status.HTTP_201_CREATED)
async def add_userlink_to_group(
    params: ParamsAddUserToGroup,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Добавить пользователя в группу

    Parameters
    ----------
    params : ParamsAddUserToGroup
        Параметры добавления пользователя в группу
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных
    """
    await add_users_to_group(
        user_id=user.id,
        to_user_ids=[params.user_id],
        group_id=params.group_id,
        session=session,
    )


@router.post("/add/users", status_code=status.HTTP_201_CREATED)
async def add_userlinks_to_group(
    params: ParamsAddUsersToGroup,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Добавить нескольких пользователей в группу

    Parameters
    ----------
    params : ParamsAddUsersToGroup
        Параметры добавления пользователей в группу
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных
    """
    await add_users_to_group(
        user_id=user.id,
        to_user_ids=params.user_ids,
        group_id=params.group_id,
        session=session,
    )


@router.patch("/rename/{group_id}", status_code=status.HTTP_201_CREATED)
async def rename_group(
    params: GroupUpdate,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
) -> GroupRead:
    """
    Переименовать группу

    Parameters
    ----------
    params : GroupUpdate
        Новое имя группы
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных

    Returns
    -------
    GroupRead
        Информация о обновленной группе
    """
    group = await select_group(group_id=params.group_id, session=session)
    if user.id not in [user.id for user in group.users]:
        raise GroupPermissionException

    renamed_group = await update_group(group=group, name=params.name, session=session)
    return renamed_group


@router.delete("/delete/user", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_from_group(
    params: ParamsDeleteUserFromGroup,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Удалить пользователя из группы

    Parameters
    ----------
    params : ParamsDeleteUserFromGroup
        Параметры для удаления пользователя из группы
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных
    """
    group = await select_group(group_id=params.group_id, session=session)
    if user.id not in [user.id for user in group.users]:
        raise GroupPermissionException

    if user.id == params.user_id:
        raise DeleteUserFromGroupException

    await remove_user_from_group(user_id=params.user_id, group=group, session=session)


@router.delete("/delete/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(async_db.get_async_session),
):
    """
    Удалить группу

    Parameters
    ----------
    group_id : int
        Идентификатор группы
    user : User
        Объект текущего пользователя
    session : AsyncSession
        Асинхронная сессия базы данных
    """
    group = await select_group(group_id=group_id, session=session)
    if user.id not in [user.id for user in group.users]:
        raise GroupPermissionException
    await remove_group(group=group, session=session)
