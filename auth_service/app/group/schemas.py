from uuid import UUID
from pydantic import BaseModel, ConfigDict


class GroupBase(BaseModel):
    """
    Базовый класс для представления данных
    о модели пользовательской группе

    Attributes
    ----------
    id : int
        Идентификатор группы
    """

    model_config = ConfigDict(from_attributes=True)  # Настройка для маппинга атрибутов
    id: int


class GroupRead(GroupBase):
    """
    Класс для запросов на чтение объектов пользовательской группы

    Attributes
    ----------
    name : str
        Название группы
    creator_id : UUID
        Идентификатор создателя группы
    """

    name: str
    creator_id: UUID


class GroupCreate(BaseModel):
    """
    Класс для создания новой объекта пользовательской группы

    Attributes
    ----------
    name : str
        Название создаваемой группы
    """

    name: str


class GroupUpdate(BaseModel):
    """
    Класс для обновления данных объекта пользовательской группы

    Attributes
    ----------
    group_id : int
        Идентификатор группы, которую нужно обновить
    name : str
        Новое имя группы
    """

    group_id: int
    name: str


class ParamsAddToGroup(BaseModel):
    """
    Базовый класс для операций, связанных с
    добавлением в группу

    Attributes
    ----------
    group_id : int
        Идентификатор группы
    """

    group_id: int


class ParamsAddUserToGroup(ParamsAddToGroup):
    """
    Класс для добавления пользователя в группу

    Attributes
    ----------
    user_id : UUID
        Идентификатор пользователя, которого нужно добавить в группу
    """

    user_id: UUID


class ParamsAddUsersToGroup(ParamsAddToGroup):
    """
    Класс для добавления нескольких пользователей в группу

    Attributes
    ----------
    user_ids : list[UUID]
        Список идентификаторов пользователей, которых нужно добавить в группу
    """

    user_ids: list[UUID]


class ParamsDeleteUserFromGroup(ParamsAddUserToGroup):
    """
    Класс для удаления пользователя из группы
    """

    pass
