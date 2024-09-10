from app.models import User, StorageFile


class StorageFilePermission:
    @staticmethod
    def check_user_access(user: User, storage_file: StorageFile) -> bool:
        if user.is_superuser:
            return True
        if user.id == storage_file.creator_id:
            return True
        if storage_file in user.files:
            return True
        return False
