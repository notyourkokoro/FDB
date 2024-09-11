import os
from app.settings import settings
from app.models import FileTypeEnum
from app.exceptions import FileNameException


class StogareController:
    basedir = settings.storage_dir

    def get_user_dir(self, user_id: str) -> str:
        dir_path = os.path.join(self.basedir, str(user_id))
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    def get_filepath(self, user_id: str, filename: str) -> str:
        filepath = os.path.join(self.get_user_dir(user_id), filename)
        if os.path.exists(filepath):
            raise FileNameException
        return filepath

    def get_filetype_id(self, filename: str) -> int:
        _, filetype = os.path.splitext(filename)
        return FileTypeEnum[filetype[1:]].value

    def rename_file(self, current_path: str, new_path: str):
        os.rename(current_path, new_path)


storage = StogareController()
