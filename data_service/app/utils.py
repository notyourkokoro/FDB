import os

import pandas as pd

from datetime import datetime

from app.settings import settings
from app.exceptions import FilepathNotFoundException, ColumnsNotFoundException


class TempStorage:
    basedir = settings.temp_dir

    @staticmethod
    def _get_name(filetype: str = "xlsx") -> str:
        return f"{round(datetime.now().timestamp() * 100000)}.{filetype}"

    @classmethod
    def get_path(cls, filename: str) -> str:
        return os.path.join(cls.basedir, filename)

    @classmethod
    def create_file(cls, df: pd.DataFrame, index=False) -> str:
        filename = cls._get_name()
        df.to_excel(cls.get_path(filename), index=index)
        return filename

    @classmethod
    def delete_file(cls, filepath: str):
        if not os.path.exists(filepath):
            raise FilepathNotFoundException
        os.remove(filepath)


class ValidateData:
    @staticmethod
    def check_columns(df: pd.DataFrame, columns: list[str] | None) -> pd.DataFrame:
        if columns:
            error_columns = set(columns) - set(df.columns)
            if len(error_columns) == 0:
                df = df[columns]
            else:
                raise ColumnsNotFoundException(columns=error_columns)
        return df
