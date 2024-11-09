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
    stmt = select(User).options(selectinload(User.groups)).where(User.id == user_id)
    user = await session.scalar(stmt)
    if user is None:
        raise UserNotFoundException
    return user


async def select_users(session: AsyncSession, user_ids: list[UUID]) -> list[User]:
    stmt = select(User).where(User.id.in_(user_ids))
    users = list(await session.scalars(stmt))

    if len(user_ids) != len(users):
        current_user_ids = [user.id for user in users]
        raise UsersNotFoundException(
            user_ids=list(filter(lambda x: x not in current_user_ids, user_ids))
        )

    return users


async def create_group(name: str, user_id: UUID, session: AsyncSession) -> Group:
    try:
        created_group = Group(creator_id=user_id, name=name)

        session.add(created_group)

        user = await select_user(user_id=user_id, session=session)
        user.groups.append(created_group)

        await session.commit()

        return created_group
    except IntegrityError:
        raise GroupExistsException


async def select_group(group_id: int, session: AsyncSession) -> Group:
    stmt = select(Group).options(selectinload(Group.users)).where(Group.id == group_id)

    group = await session.scalar(stmt)
    if group is None:
        raise GroupNotFoundException
    return group


async def select_user_groups(user_id: UUID, session: AsyncSession) -> Sequence[Group]:
    user = await select_user(user_id=user_id, session=session)
    return user.groups


async def add_users_to_group(
    user_id: UUID, to_user_ids: list[UUID], group_id: int, session: AsyncSession
):
    group = await select_group(group_id=group_id, session=session)

    if user_id not in [user.id for user in group.users]:
        raise GroupPermissionException

    users = await select_users(session=session, user_ids=to_user_ids)

    users_with_group = []
    for user in users:
        if user in group.users:
            users_with_group.append(user.id)

    if len(users_with_group) != 0:
        raise UsersInGroupExistsException(users_with_group)

    group.users.extend(list(users))
    await session.commit()


async def update_group(group: Group, name: str, session: AsyncSession) -> Group:
    try:
        stmt = update(Group).where(Group.name == group.name).values(name=name)

        await session.execute(stmt)
        await session.commit()
        await session.refresh(group)

        return group
    except IntegrityError:
        raise GroupExistsException


async def remove_group(group: Group, session: AsyncSession):
    await session.delete(group)
    await session.commit()


async def remove_user_from_group(group: Group, user_id: UUID, session: AsyncSession):
    user = await select_user(user_id=user_id, session=session)
    if user not in group.users:
        raise ContaionsUserInGroupException

    group.users.remove(user)
    await session.commit()
