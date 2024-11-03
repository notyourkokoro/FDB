import os
from app.settings import settings
from app.models import FileTypeEnum
from app.exceptions import FileNameException, FilepathNotFoundException


class StogareController:
    basedir = settings.storage_dir

    @classmethod
    def get_user_dir(cls, user_id: str, version: int | str = 1) -> str:
        dir_path = os.path.join(cls.basedir, str(user_id), str(version))
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    @classmethod
    def get_filepath(cls, user_id: str, filename: str, version: int | str = 1) -> str:
        filepath = os.path.join(cls.get_user_dir(user_id, version), filename)
        if os.path.exists(filepath):
            raise FileNameException
        return filepath

    @staticmethod
    def get_filetype_id(filename: str) -> int:
        _, filetype = os.path.splitext(filename)
        return FileTypeEnum[filetype[1:]].value

    @staticmethod
    def get_filename_based_on(filename_left: str, filename_right: str) -> str:
        filename_cut, _ = os.path.splitext(filename_left)
        _, filetype = os.path.splitext(filename_right)  # возвращает тип вместе с точкой
        return filename_cut + filetype

    @staticmethod
    def create_file(filepath: str, file_obj):
        with open(filepath, "wb") as output_file:
            output_file.write(file_obj.read())

    @staticmethod
    def create_based_on(filepath_read: str, filepath_output: str):
        if not os.path.exists(filepath_read):
            raise FilepathNotFoundException

        if os.path.exists(filepath_output):
            raise FileExistsError

        with open(filepath_read, "rb") as read_file:
            StogareController.create_file(filepath_output, read_file)

    @staticmethod
    def rename_file(current_path: str, new_path: str):
        os.rename(current_path, new_path)

    @staticmethod
    def delete_file(filepath: str):
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)
