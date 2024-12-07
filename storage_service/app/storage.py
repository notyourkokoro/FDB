import os
from app.settings import settings
from app.models import FileTypeEnum
from app.exceptions import FileNameException, FilepathNotFoundException


class StogareController:
    """
    Класс для работы с файловым хранилищем.
    Управляет директориями и файлами

    Parameters
    ----------
    basedir : str
        Путь к директории хранилища
    """

    basedir = settings.storage_dir

    @classmethod
    def get_user_dir(cls, user_id: str, version: int | str = 1) -> str:
        """
        Получение пути к директории пользователя для хранения файлов с учётом версии

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя
        version : int | str, optional
            Версия файлов (по умолчанию 1)

        Returns
        -------
        str
            Путь к директории пользователя для указанной версии
        """
        # Получение пути к директории пользователя
        dir_path = os.path.join(cls.basedir, str(user_id), str(version))
        # Создание директории, если она не существует
        os.makedirs(dir_path, exist_ok=True)
        return dir_path

    @classmethod
    def get_filepath(cls, user_id: str, filename: str, version: int | str = 1) -> str:
        """
        Получение пути к файлу пользователя с проверкой на существование

        Parameters
        ----------
        user_id : str
            Идентификатор пользователя
        filename : str
            Имя файла
        version : int | str, optional
            Версия файла (по умолчанию 1)

        Raises
        ------
        FileNameException
            Если файл с таким именем уже существует, рейсится исключение

        Returns
        -------
        str
            Путь к файлу
        """
        # Получение пути к файлу
        filepath = os.path.join(cls.get_user_dir(user_id, version), filename)
        # Проверка файла на существование
        if os.path.exists(filepath):
            raise FileNameException
        return filepath

    @staticmethod
    def get_filetype_id(filename: str) -> int:
        """
        Получение идентификатора типа файла по расширению

        Parameters
        ----------
        filename : str
            Имя файла

        Returns
        -------
        int
            Идентификатор типа файла, соответствующий его расширению
        """
        _, filetype = os.path.splitext(filename)
        return FileTypeEnum[filetype[1:]].value

    @staticmethod
    def get_filename_based_on(filename_left: str, filename_right: str) -> str:
        """
        Формирование имени файла для новой версии на основе двух имен файлов

        Parameters
        ----------
        filename_left : str
            Имя исходного файла
        filename_right : str
            Имя файла, на основе которого создается новый файл

        Returns
        -------
        str
            Имя нового файла
        """
        # Получение имени файла без расширения
        filename_cut, _ = os.path.splitext(filename_left)
        # Получение типа файла вместе с точкой
        _, filetype = os.path.splitext(filename_right)
        return filename_cut + filetype

    @staticmethod
    def create_file(filepath: str, file_obj):
        """
        Создание файла по указанному пути

        Parameters
        ----------
        filepath : str
            Путь, по которому будет сохранён файл
        file_obj : file-like object
            Объект файла, который нужно записать
        """
        with open(filepath, "wb") as output_file:
            output_file.write(file_obj.read())

    @staticmethod
    def create_based_on(filepath_read: str, filepath_output: str):
        """
        Создание нового файла на основе существующего (копирование)

        Parameters
        ----------
        filepath_read : str
            Путь к исходному файлу
        filepath_output : str
            Путь для нового файла

        Raises
        ------
        FilepathNotFoundException
            Если исходный файл не найден - ошибка
        FileExistsError
            Если новый файл уже существует - ошибка
        """
        # Проверка наличия исходного файла
        if not os.path.exists(filepath_read):
            raise FilepathNotFoundException

        # Проверка на отсутствие пути для нового файла
        if os.path.exists(filepath_output):
            raise FileExistsError

        # Запись нового файла
        with open(filepath_read, "rb") as read_file:
            StogareController.create_file(filepath_output, read_file)

    @staticmethod
    def rename_file(current_path: str, new_path: str):
        """
        Переименование файла

        Parameters
        ----------
        current_path : str
            Текущий путь файла
        new_path : str
            Новый путь файла
        """
        os.rename(current_path, new_path)

    @staticmethod
    def delete_file(filepath: str):
        """
        Удаление файла по указанному пути

        Parameters
        ----------
        filepath : str
            Путь к файлу, который нужно удалить

        Raises
        ------
        FilepathNotFoundException
            Если файл не найден
        """
        # Проверка файла на существование по указанному пути
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)
