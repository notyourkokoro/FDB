import pandas as pd
import numpy as np
import statsmodels.api as sm

from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from app.statistic.exceptions import (
    BASE_PRINT,
    BinaryColumnsException,
    EmptyColumnException,
    NanColumnsException,
)
from app.statistic.schemas import ClusteringMethod


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


class OutliersBuilder:
    @classmethod
    def _calculate_z_score(cls, df: pd.DataFrame) -> pd.DataFrame:
        return stats.zscore(df, nan_policy="omit")

    @classmethod
    def _calculate_modified_z_score(cls, df: pd.DataFrame) -> pd.DataFrame:
        median = df.median()
        mad = (df - median).abs().median()

        return 0.6745 * (df - median) / (mad + 1e-5)

    @classmethod
    def _calculate_iqr(cls, df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        q1 = df.quantile(0.25)
        q3 = df.quantile(0.75)
        iqr = q3 - q1
        lower_bound, upper_bound = q1 - (1.5 * iqr), q3 + (1.5 * iqr)
        return lower_bound, upper_bound

    @classmethod
    def _calculate_iso_forest(
        cls,
        df: pd.DataFrame,
        contamination: float = 0.1,
        seed: int = 14,
    ) -> list[int]:
        model = IsolationForest(contamination=contamination, random_state=seed)
        model.fit(df)
        outliers = model.predict(df)
        return outliers

    @classmethod
    def z_score(
        cls, df: pd.DataFrame, y_column: str | None = None, threshold: float = 3
    ) -> pd.Series:
        df_for_outliers = np.abs(cls._calculate_z_score(df))
        if y_column is not None:
            df_for_outliers = df_for_outliers[[y_column]]
        return (df_for_outliers > threshold).any(axis=1).astype(int)

    @classmethod
    def modified_z_score(
        cls, df: pd.DataFrame, y_column: str | None = None, threshold: float = 3.5
    ) -> pd.Series:
        df_for_outliers = cls._calculate_modified_z_score(df)
        if y_column is not None:
            df_for_outliers = df_for_outliers[[y_column]]
        return (df_for_outliers > threshold).any(axis=1).astype(int)

    @classmethod
    def iqr(cls, df: pd.DataFrame, y_column: str | None = None) -> pd.Series:
        if y_column is not None:
            df = df[[y_column]]
        lower_bound, upper_bound = cls._calculate_iqr(df)
        return ((df < lower_bound) | (df > upper_bound)).any(axis=1).astype(int)

    @classmethod
    def iso_forest(cls, df: pd.DataFrame, y_column: str | None = None) -> list[int]:
        if y_column is not None:
            df = df[[y_column]]

        columns_with_nan = df.columns[df.isna().any()].tolist()
        if len(columns_with_nan) != 0:
            raise NanColumnsException(columns_with_nan)
        outliers = cls._calculate_iso_forest(df)
        return [1 if outlier == -1 else 0 for outlier in outliers]

    @classmethod
    def build(
        cls,
        df: pd.DataFrame,
        method_name: str,
        y_column: str | None = None,
    ) -> dict[str, list[int]]:
        """
        Класс для определения выбросов в данных при помощи
        различных методов

        Parameters
        ----------
        df : pd.DataFrame
            Данные, которые необходимо учитывать
            при поиске выбросов
        method_name : str
            Имя метода, при помощи которого будут
            определены выбросы
        y_column : str | None, optional
            Имя поля, в котором необходимо найти выбросы.
            В случае, если поле не указано, поиск выбросов
            производится во всем DataFrame

        Returns
        -------
        dict[str, list[int]]
            Словарь с именем колонки и данными о выбросах.
            В имени колонки будет содердать не только имя
            метода для определения выбросов, но и y_column,
            если оно имеет значение отличное от None
        """
        func = getattr(cls, method_name)
        outliers = func(df, y_column)
        if isinstance(outliers, pd.Series):
            outliers = outliers.to_list()
        name = f"{method_name}_outliers{f"_{y_column}" if y_column is not None else ""}"
        return {name: outliers}


class CorrBuilder:
    headers = [
        "Pair of columns",
        "Valid N",
        "Spearman R",
        "p-value",
    ]

    @classmethod
    def build(
        cls,
        df: pd.DataFrame,
        left_columns: list[str],
        right_columns: list[str],
        round_value: int = 2,
        dropna: bool = True,
    ) -> pd.DataFrame:
        result = []
        for left_col in left_columns:
            for right_col in right_columns:
                # удаляем нулевые значения, чтобы не было NaN
                temp_df = df[[left_col, right_col]]
                if dropna is True:
                    temp_df.dropna(inplace=True)
                n = len(temp_df)
                # коэффициент и p-value ранговой корреляции Спирмена
                rho, p = stats.spearmanr(temp_df[left_col], temp_df[right_col])
                result.append(
                    [
                        f"{left_col} / {right_col}",
                        n,
                        str(round(rho, round_value)),
                        str(round(p, round_value)),
                    ]
                )

        return pd.DataFrame(result, columns=cls.headers)


class ClustersBuilder:
    @classmethod
    def _get_name(cls, method: ClusteringMethod) -> str:
        return f"{method.value}_clusters"

    @classmethod
    def _data_standardization(cls, df: pd.DataFrame) -> np.ndarray:
        scaler = StandardScaler()
        df_normalized = scaler.fit_transform(df)
        return df_normalized

    @staticmethod
    def kmeans(df: pd.DataFrame, n_clusters: int, seed: int = 14) -> pd.DataFrame:
        model = KMeans(n_clusters=n_clusters, random_state=seed)
        df_normalized = ClustersBuilder._data_standardization(df)

        return model.fit_predict(df_normalized)

    @classmethod
    def build(
        cls,
        df: pd.DataFrame,
        method: ClusteringMethod,
        n_clusters: int = 3,
    ) -> dict[str, int]:
        func = getattr(cls, method.value)
        result = func(df=df, n_clusters=n_clusters)
        name = cls._get_name(method)

        return {name: result.tolist()}


class ORBuilder:
    binary_set = {0, 1}

    def _is_binary(self, sr: pd.Series) -> bool:
        sr = sr.dropna()
        unique_vals = set(sr.unique())

        return unique_vals.issubset(self.binary_set)

    def _to_binary(self, sr: pd.Series) -> pd.Series:
        # Определяем максимальное и минимальное значения
        max_value = sr.max()
        min_value = sr.min()

        # Заменяем максимальные значения на 1, минимальные на 0
        sr = sr.where(sr != max_value, 1).where(sr != min_value, 0)

        return sr

    def _set_datas(self):
        self.datas = dict()
        for i in range(2):
            split_data = self._df[self._df[self.split_column] == i]

            name = f"{self.split_column} == {i} (N = {len(split_data)})"
            self.datas[name] = split_data
            self.result[name] = []

        self.result["ОШ 95% ДИ"] = []

    def _calulate(self):
        for col in self._df.columns:
            if col == self.target_column or col == self.split_column:
                continue
            try:
                current_df = self._df[[col, self.target_column]]
                # удаление строк с пустыми ячейками
                current_df = current_df.dropna()

                # разбивка данных для модели
                X = current_df[col]
                y = current_df[self.target_column]

                # добавление константы для интерсепта
                X = sm.add_constant(X)

                # создание модели
                model = sm.Logit(y, X)
                fit_model = model.fit()

                # формирование результата
                local_result = fit_model.conf_int()
                local_result["OR"] = fit_model.params
                local_result.columns = ["2.5%", "97.5%", "OR"]
                local_result = round(np.exp(local_result), 3)

                # добавление результата в отчет
                self.result["ОШ 95% ДИ"].append(
                    f"{local_result["OR"][col]} ({local_result["2.5%"][col]}; {local_result["97.5%"][col]})"
                )

            except Exception as e:
                self.result["ОШ 95% ДИ"].append("N/A")
                print(e)

            for name, dict_data in self.datas.items():
                self.result[name].append(
                    f"{len(dict_data[col].dropna())}/{len(dict_data)}"
                )
            self.add_rows.append(col)

    def __init__(self, df: pd.DataFrame, target_column: str, split_column: str):
        self._df = df
        self.target_column = target_column
        self.split_column = split_column

    def build(self) -> dict[str, list[str]]:
        self.add_rows = []
        self.result = {"Колонки": self.add_rows}

        self._set_datas()

        error_columns = []
        for column in (self.target_column, self.split_column):
            if not self._is_binary(self._df[column]):
                error_columns.append(column)

        if len(error_columns) != 0:
            raise BinaryColumnsException(columns=error_columns)

        self._calulate()

        return self.result
