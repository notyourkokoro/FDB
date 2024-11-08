import pandas as pd

from sklearn.impute import KNNImputer

from app.exceptions import ColumnsNotFoundException
from app.statistic.exceptions import (
    BadGroupParamsException,
    BadOperationException,
)


class DataBuilder:
    operations = {">", "<", ">=", "<=", "==", "!="}

    @classmethod
    def _get_value(cls, value: str) -> str | float | int:
        if value.isdigit():
            return int(value)

        if value.replace(".", "", 1).isdigit():
            return float(value)

        return value

    @classmethod
    def create_group(
        cls, df: pd.DataFrame, params: dict[str, str | int]
    ) -> tuple[str, pd.DataFrame]:
        if len(params) != 3:
            raise BadGroupParamsException

        column, operation, value = params.values()
        value = cls._get_value(value)

        if column not in df.columns:
            raise ColumnsNotFoundException([column])

        if operation not in cls.operations:
            raise BadOperationException(cls.operations)

        if operation != "==" and isinstance(value, str):
            raise BadOperationException(operations=["=="], value_type="str")

        return (
            f"{column} {operation} {value}",
            eval(f"df[df[{repr(column)}] {operation} {repr(value)}]"),
        )

    @classmethod
    def build(
        cls,
        df: pd.DataFrame,
        groups: list[dict[str, str | int]] | None = None,
    ) -> dict[str, pd.DataFrame]:
        datas = {"all": df}

        if groups is not None:
            for group in groups:
                name, data = cls.create_group(df, group)
                datas[name] = data

        return datas


class RecoveryDataBuilder:
    @classmethod
    def knn(cls, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        if kwargs.get("n_neighbors") is None:
            n_neighbors = 5
        else:
            n_neighbors = kwargs["n_neighbors"]

        imputer = KNNImputer(n_neighbors=n_neighbors)
        imputer.set_output(transform="pandas")
        result = imputer.fit_transform(df)
        # преобразование типов к изначальному виду
        result = result.astype(df.dtypes)
        return result

    @classmethod
    def recovery(cls, df: pd.DataFrame, method_name: str, **kwargs) -> pd.DataFrame:
        func = getattr(cls, method_name)
        result = func(df, **kwargs)
        return result
