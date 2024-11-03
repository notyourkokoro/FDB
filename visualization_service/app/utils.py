import os
import matplotlib.pyplot as plt

from datetime import datetime
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.settings import settings
from app.exceptions import FilepathNotFoundException
from app.schemas import ImageFormat, ImageMediaType


class TempStorage:
    basedir = settings.temp_dir

    @staticmethod
    def get_name(filetype: ImageFormat = ImageFormat.PNG) -> str:
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype.value}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        return os.path.join(cls.basedir, filename)

    @classmethod
    def create_file(
        cls,
        filetype: ImageFormat = ImageFormat.PNG,
    ) -> str:
        filename = cls.get_name(filetype)
        filepath = cls.get_path(filename)

        plt.savefig(filepath)
        # Удаление из временной памяти изображения
        plt.close()

        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)

    @classmethod
    def return_file(
        cls,
        save_format: ImageFormat = ImageFormat.PNG,
    ) -> FileResponse:
        filename = cls.create_file(filetype=save_format)
        filepath = cls.get_path(filename)
        media_type = getattr(ImageMediaType, save_format.name).value

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type,
            background=BackgroundTask(cls.delete_file, filepath=filepath),
        )
