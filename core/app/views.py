from sqladmin import ModelView

from app.storage_service.models import (  # noqa F401 - необходимо для корректной работы
    UserFile,
    FileType,
    StorageFile,
)
from app.auth_service.models import User, Group


class UserView(ModelView, model=User):
    """
    Вью ORM-модели пользователя для админ-панели
    """

    column_list = [User.id, User.email, User.is_active, User.is_superuser]


class FileTypeView(ModelView, model=FileType):
    """
    Вью ORM-модели типов файлов для админ-панели
    """

    column_list = [FileType.id, FileType.name]


class StorageFileView(ModelView, model=StorageFile):
    """
    Вью ORM-модели загружаемого пользователем файла для админ-панели
    """

    column_list = [
        StorageFile.id,
        StorageFile.filename,
        StorageFile.type_id,
        StorageFile.size,
    ]


class GroupView(ModelView, model=Group):
    """
    Вью ORM-модели пользовательной группы для админ-панели
    """

    column_list = [Group.id, Group.creator_id, Group.name]
