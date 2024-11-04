import pandas as pd

from app.exceptions import ColumnsNotFoundException, NotNumericTypeException


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

    @staticmethod
    def check_numeric_type(df: pd.DataFrame, columns: list[str]):
        error_columns = []
        for column in columns:
            if not pd.api.types.is_numeric_dtype(df[column]):
                error_columns.append(column)
        if len(error_columns) != 0:
            raise NotNumericTypeException(columns=error_columns)
