from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StorageFileBase(BaseModel):
    id: int
    filename: str


class StorageFileRead(StorageFileBase):
    model_config = ConfigDict(from_attributes=True)

    creator_id: UUID
    path: str
    size: int
    type_id: int
    upload_date: datetime
    update_date: datetime


class StorageFileList(StorageFileBase):
    creator_id: UUID


class StorageFilePatch(BaseModel):
    filename: str


class AddUserFile(BaseModel):
    to_user_id: str
    file_id: int
