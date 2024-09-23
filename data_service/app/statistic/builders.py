import pandas as pd

from app.statistic.exceptions import (
    BASE_PRINT,
    BadGroupParamsException,
    BadOperationException,
    ColumnsNotFoundException,
    EmptyColumnException,
)


class DescriptiveStatisticsBuilder:
    binary_set = {0, 1}

    @classmethod
    def _is_binary(cls, sr: pd.Series) -> bool:
        sr = sr.dropna()
        unique_vals = set(sr.unique())

        return unique_vals.issubset(cls.binary_set)

    @classmethod
    def full_row(cls, sr: pd.Series, round_value: int = 2) -> str:
        try:
            return "{mean}±{std}; {median} ({quantile_25}; {quantile_75}) {minimum}-{maximum}".format(
                mean=round(sr.mean(), round_value),
                std=round(sr.std(), round_value),
                median=round(sr.median(), round_value),
                quantile_25=round(sr.quantile(0.25), round_value),
                quantile_75=round(sr.quantile(0.75), round_value),
                minimum=round(sr.min(), round_value),
                maximum=round(sr.max(), round_value),
            )
        except Exception as e:
            print(
                BASE_PRINT.format(
                    name=cls.descriptive_row.__name__, data=sr.tolist(), error=e
                )
            )
            return "-"

    @classmethod
    def cut_row(cls, sr: pd.Series, include_nan: bool = True) -> str:
        true_data = sr[sr == 1]

        if include_nan is True:
            n = len(sr)
        else:
            n = len(sr[sr == 0]) + len(true_data)

        # если есть хотя бы одна строка в выбранном столбце,
        # которая имеет значение 1
        if len(true_data) > 0:
            true_count = len(true_data)

            # считается количество строк в столбце, которые равны единице
            # данное значение подставляется в начало строки,
            # после подставляется количество строк во всей выборке
            # в конце рассчитываются проценты по ранее рассчитанным данным
            # (количество ненулевых строк умножается на 100 и делится на
            # общий объем выборки)
            return "{count}/{n} ({result}%)".format(
                count=true_count, n=n, result=round(true_count * 100 / n, 2)
            )
        elif n > 0:
            # число ненулевых значений в столбце указывается равным нулю,
            # подставляется чисто строк в выборке, проценты отмечаются нулем
            return "0/{n} (0%)".format(n=n)
        return "-"

    @classmethod
    def build(
        cls, datas: dict[str, pd.DataFrame], include_nan: bool = True
    ) -> dict[str, list[str]]:
        result = {"columns": list(datas["all"].columns)}

        for name, data in datas.items():
            column_result = []
            for column in data.columns:
                sr = data[column]
                if len(sr.dropna()) == 0:
                    raise EmptyColumnException(column=column)

                if cls._is_binary(sr):
                    column_result.append(cls.cut_row(sr))
                else:
                    column_result.append(cls.full_row(sr, include_nan))

            result[name] = column_result

        return result


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
