import os
import pandas as pd

from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.settings import settings
from app.exceptions import FilepathNotFoundException
from app.schemas import DataFormat, DataMediaType


class TempStorage:
    """
    Класс для работы с временным хранилищем файлов

    Attributes
    ----------
    basedir : str
        Директория для хранения временных файлов
    """

    basedir = settings.temp_dir

    @staticmethod
    def get_name(filetype: DataFormat = DataFormat.XLSX) -> str:
        """
        Генерирует уникальное имя для файла
        на основе текущего времени и типа файла

        Parameters
        ----------
        filetype : DataFormat, optional
            Формат файла, по умолчанию XLSX

        Returns
        -------
        str
            Сгенерированное имя файла с расширением
        """
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype.value}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        """
        Получает полный путь ко временному файлу хранилище

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
        df: pd.DataFrame,
        filetype: DataFormat = DataFormat.XLSX,
        index=False,
    ) -> str:
        """
        Создает временный файл с данными

        Parameters
        ----------
        df : pd.DataFrame
            Данные для записи в файл
        filetype : DataFormat, optional
            Формат файла (CSV или XLSX), по умолчанию XLSX
        index : bool, optional
            Нужно ли сохранять индексы строк, по умолчанию False

        Returns
        -------
        str
            Имя созданного файла
        """
        # Генерация имени файла и пути
        filename = cls.get_name(filetype)
        filepath = cls.get_path(filename)

        # Запись данных во временный файл в зависимости от формата
        if filetype == DataFormat.CSV:
            df.to_csv(filepath, encoding="utf-8", index=index)
        else:
            df.to_excel(filepath, index=index)
        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        """
        Удаляет временный файл, если он существует,
        иначе возбуждает исключение

        Parameters
        ----------
        filepath : str
            Путь к файлу для удаления

        Raises
        ------
        FilepathNotFoundException
            Если файл не найден - исключение
        """
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)

    @classmethod
    def return_file(
        cls,
        df: pd.DataFrame,
        save_format: DataFormat = DataFormat.XLSX,
        index=False,
    ) -> FileResponse:
        """
        Создает временный файл с данными,
        возвращает его в ответе, а также
        запускает задачу на его удаление
        после отправки

        Parameters
        ----------
        df : pd.DataFrame
            Данные для записи в файл
        save_format : DataFormat, optional
            Формат сохраненного файла (CSV или XLSX), по умолчанию XLSX
        index : bool, optional
            Нужно ли сохранять индексы строк, по умолчанию False

        Returns
        -------
        FileResponse
            Ответ с файлом для получения пользователем
        """
        # Генерация имени файла и пути
        filename = cls.create_file(df=df, filetype=save_format, index=index)
        filepath = cls.get_path(filename)
        # Определение типа контента для файла
        media_type = getattr(DataMediaType, save_format.name).value

        # Возвращение файла в ответе с фоновым удалением после отправки
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=filepath),
        )
