from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GroupBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class GroupRead(GroupBase):
    name: str
    creator_id: UUID


class GroupCreate(BaseModel):
    name: str


class GroupUpdate(BaseModel):
    group_id: int
    name: str


class ParamsAddToGroup(BaseModel):
    group_id: int


class ParamsAddUserToGroup(ParamsAddToGroup):
    user_id: UUID


class ParamsAddUsersToGroup(ParamsAddToGroup):
    user_ids: list[UUID]


class ParamsDeleteUserFromGroup(ParamsAddUserToGroup):
    pass
