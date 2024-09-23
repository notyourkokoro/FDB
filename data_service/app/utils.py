import os

import pandas as pd

from datetime import datetime

from app.settings import settings
from app.exceptions import FilepathNotFoundException


class TempStorage:
    basedir = settings.temp_dir

    @staticmethod
    def _get_name(filetype: str = "xlsx") -> str:
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        return os.path.join(cls.basedir, filename)

    @classmethod
    def create_file(cls, df: pd.DataFrame) -> str:
        filename = cls._get_name()
        df.to_excel(cls.get_path(filename), index=False)
        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)
