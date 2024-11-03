import pandas as pd

from typing import Counter

from app.exceptions import ColumnsNotFoundException
from app.exceptions import ColumnsDuplicateException


class ValidateData:
    @staticmethod
    def check_columns(df: pd.DataFrame, columns: list[str] | None) -> pd.DataFrame:
        if columns:
            error_columns = set(columns) - set(df.columns)
            if len(error_columns) == 0:
                df = df[columns]
            else:
                raise ColumnsNotFoundException(columns=list(error_columns))
        return df


class CorrelationValidation:
    @staticmethod
    def validate(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        column_count = Counter(columns)
        columns_set = set(filter(lambda col: column_count[col] > 1, column_count))
        if len(columns_set) > 1:
            raise ColumnsDuplicateException(columns=columns_set)

        df = ValidateData.check_columns(df=df, columns=columns)

        return df
