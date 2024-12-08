import os
import matplotlib.pyplot as plt

from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.settings import settings
from app.exceptions import FilepathNotFoundException
from app.schemas import ImageFormat, ImageMediaType


class TempStorage:
    """
    Класс для работы с временным хранилищем изображений

    Attributes
    ----------
    basedir : str
        Путь к директории для хранения временных файлов
    """

    basedir = settings.temp_dir

    @staticmethod
    def get_name(filetype: ImageFormat = ImageFormat.PNG) -> str:
        """
        Генерирует уникальное имя файла на основе текущего времени

        Parameters
        ----------
        filetype : ImageFormat
            Формат изображения (по умолчанию PNG)

        Returns
        -------
        str
            Уникальное имя файла с расширением
        """
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype.value}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        """
        Возвращает полный путь к файлу

        Parameters
        ----------
        filename : str
            Имя файла

        Returns
        -------
        str
            Полный путь к файлу
        """
        return os.path.join(cls.basedir, filename)

    @classmethod
    def create_file(
        cls,
        filetype: ImageFormat = ImageFormat.PNG,
    ) -> str:
        """
        Создает файл изображения и сохраняет его во временное хранилище

        Parameters
        ----------
        filetype : ImageFormat
            Формат изображения (по умолчанию PNG)

        Returns
        -------
        str
            Имя сохраненного файла
        """
        # Генерация имени файла и пути
        filename = cls.get_name(filetype)
        filepath = cls.get_path(filename)

        # Сохранение изображения в файл
        plt.savefig(filepath)
        # Удаление из временной памяти изображения
        plt.close()

        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        """
        Удаляет файл по указанному пути

        Parameters
        ----------
        filepath : str
            Путь к файлу для удаления

        Raises
        ------
        FilepathNotFoundException
            Если файл не найден - рейсится ошибка
        """
        # Проверка файла на существование
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)

    @classmethod
    def return_file(
        cls,
        save_format: ImageFormat = ImageFormat.PNG,
    ) -> FileResponse:
        """
        Создает и возвращает изображение в формате FileResponse

        Parameters
        ----------
        save_format : ImageFormat
            Формат изображения для сохранения (по умолчанию PNG)

        Returns
        -------
        FileResponse
            Ответ со ссылкой на файлом изображения
        """
        # Генерация имени файла и пути
        filename = cls.create_file(filetype=save_format)
        filepath = cls.get_path(filename)
        # Определение типа медиа-файла
        media_type = getattr(ImageMediaType, save_format.name).value

        # Возвращение файла с изображением
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=filepath),
        )
