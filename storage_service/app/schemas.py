from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StorageFileBase(BaseModel):
    """
    Базовая модель для представления файлов

    Parameters
    ----------
    id : int
        Идентификатор файла
    filename : str
        Имя файла
    """

    id: int
    filename: str


class StorageFileRead(StorageFileBase):
    """
    Схема для представления файла с дополнительной информацией

    Parameters
    ----------
    creator_id : UUID
        Идентификатор создателя файла
    path : str
        Путь к файлу
    size : int
        Размер файла
    type_id : int
        Идентификатор типа файла
    upload_date : datetime
        Дата загрузки файла
    update_date : datetime
        Дата последнего обновления файла
    version : int
        Версия файла
    """

    model_config = ConfigDict(from_attributes=True)

    creator_id: UUID
    path: str
    size: int
    type_id: int
    upload_date: datetime
    update_date: datetime
    version: int


class StorageFileReadFull(StorageFileRead):
    """
    Схема для представления полного описания файла,
    включая информацию о исходном файл

    Parameters
    ----------
    version : int
        Версия файла
    based_on_id : int | None
        Идентификатор исходного файла, если он существует
    """

    version: int
    based_on_id: int | None


class StorageFileList(StorageFileBase):
    """
    Схема для представления списка файлов

    Parameters
    ----------
    creator_id : UUID
        Идентификатор создателя файла
    version : int
        Версия файла
    based_on_id : int | None
        Идентификатор исходного файла, если он существует
    """

    creator_id: UUID
    version: int
    based_on_id: int | None


class StorageFilePatch(BaseModel):
    """
    Схема для изменения информации о файле

    Parameters
    ----------
    filename : str
        Новое имя файла
    """

    filename: str


class AddUserFile(BaseModel):
    """
    Схема для добавления связи между файлом и пользователем

    Parameters
    ----------
    to_user_id : UUID
        Идентификатор пользователя, которому нужно предоставить доступ к файлу
    file_id : int
        Идентификатор файла, к которому нужно предоставить доступ
    """

    to_user_id: UUID
    file_id: int


class AddUsersFile(BaseModel):
    """
    Схема для добавления свяжей между файлом и несколькоми пользователям

    Parameters
    ----------
    to_user_ids : list[UUID]
        Список идентификаторов пользователей, которым нужно предоставить доступ к файлу
    file_id : int
        Идентификатор файла, к которому пользователям нужно предоставить доступ
    """

    to_user_ids: list[UUID]
    file_id: int


class DeleteUserFile(AddUserFile):
    """
    Схема для удаления доступа пользователя к файлу
    Наследуется от AddUserFile
    """

    pass


class AddGroupFile(BaseModel):
    """
    Схема для добавления связи между файлом и группой

    Parameters
    ----------
    group_id : int
        Идентификатор группы, к которой нужно привязать файл
    file_id : int
        Идентификатор файла, к которому нужно предоставить доступ в группе
    """

    group_id: int
    file_id: int


class DeleteGroupFile(AddGroupFile):
    """
    Схема для удаления связи файла с группой
    Наследуется от AddGroupFile
    """

    pass
