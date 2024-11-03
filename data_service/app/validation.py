import pandas as pd

from app.exceptions import ColumnsNotFoundException


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
