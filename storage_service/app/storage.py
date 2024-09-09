import os
from app.settings import settings
from app.models import FileTypeEnum


class StogareController:
    basedir = settings.storage_dir

    def get_user_dir(self, user_id: str) -> str:
        dir_path = os.path.join(self.basedir, str(user_id))
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def get_filepath(self, user_id: str, filename: str) -> str:
        return os.path.join(self.get_user_dir(user_id), filename)

    def get_filetype_id(self, filename: str) -> int:
        _, filetype = os.path.splitext(filename)
        return FileTypeEnum[filetype[1:]].value


storage = StogareController()
