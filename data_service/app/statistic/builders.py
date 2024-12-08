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
    """
    Класс для построения описательной статистики по данным

    Attributes
    ----------
    binary_set : set
        Множество бинарных значений (0, 1)
    """

    binary_set = {0, 1}

    @classmethod
    def _is_binary(cls, sr: pd.Series) -> bool:
        """
        Проверка, является ли столбец бинарным
        (содержит только 0 и 1)

        Parameters
        ----------
        sr : pd.Series
            Столбец данных

        Returns
        -------
        bool
            True, если столбец бинарный, иначе False
        """
        sr = sr.dropna()
        unique_vals = set(sr.unique())

        return unique_vals.issubset(cls.binary_set)

    @classmethod
    def full_row(cls, sr: pd.Series, round_value: int = 2) -> str:
        """
        Формирование строки описательной
        статистики для непрерывных данных

        Parameters
        ----------
        sr : pd.Series
            Столбец данных
        round_value : int, optional
            Количество знаков после запятой
            (по умолчанию 2)

        Returns
        -------
        str
            Строка с описательной статистикой
        """
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
        """
        Формирование строки статистики
        для бинарных данных (0 и/или 1)

        Parameters
        ----------
        sr : pd.Series
            Столбец данных
        include_nan : bool, optional
            Включать ли NaN значения в
            расчет (по умолчанию True)

        Returns
        -------
        str
            Строка со статистикой для бинарных данных
        """
        # Получение ненулевых строк
        true_data = sr[sr == 1]

        # Расчет количество строк в выбранном столбце
        if include_nan is True:
            n = len(sr)
        else:
            n = len(sr[sr == 0]) + len(true_data)

        # Если есть хотя бы одна строка в выбранном столбце,
        # которая имеет значение 1
        if len(true_data) > 0:
            true_count = len(true_data)

            # Считается количество строк в столбце, которые равны единице
            # данное значение подставляется в начало строки,
            # после подставляется количество строк во всей выборке
            # в конце рассчитываются проценты по ранее рассчитанным данным
            # (количество ненулевых строк умножается на 100 и делится на
            # общий объем выборки)
            return "{count}/{n} ({result}%)".format(
                count=true_count, n=n, result=round(true_count * 100 / n, 2)
            )
        elif n > 0:
            # Число ненулевых значений в столбце указывается равным нулю,
            # подставляется чисто строк в выборке, проценты отмечаются нулем
            return "0/{n} (0%)".format(n=n)
        return "-"

    @classmethod
    def build(
        cls, datas: dict[str, pd.DataFrame], include_nan: bool = True
    ) -> dict[str, list[str]]:
        """
        Генерация описательной статистики
        для всех столбцов данных

        Parameters
        ----------
        datas : dict[str, pd.DataFrame]
            Данные для анализа, где ключ — это группы
            данных, а значение — это DataFrame
        include_nan : bool, optional
            Включать ли NaN значения в расчет
            статистики (по умолчанию True)

        Returns
        -------
        dict[str, list[str]]
            Словарь с описательной статистикой
            для каждого группы ("all" — всегда по умолчанию)
        """
        # Всегда есть группа с полным DataFrame
        result = {"columns": list(datas["all"].columns)}

        # Генерация описательной статистики
        for name, data in datas.items():
            column_result = []
            for column in data.columns:
                # Проверка, является ли столбец бинарным
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
    """
    Класс для определения выбросов в
    данных с использованием различных методов
    """

    @classmethod
    def _calculate_z_score(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет z-оценки

        Parameters
        ----------
        df : pd.DataFrame
            Данные, для которых необходимо
            определить выбросы

        Returns
        -------
        pd.DataFrame
            z-оценки для всех строк в DataFrame
        """
        return stats.zscore(df, nan_policy="omit")

    @classmethod
    def _calculate_modified_z_score(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Расчет модифицированной
        z-оценки (по медиане)

        Parameters
        ----------
        df : pd.DataFrame
            Данные, для которых необходимо
            определить выбросы

        Returns
        -------
        pd.DataFrame
            Модифицированные z-оценки
            для всех строк в DataFrame
        """
        median = df.median()
        mad = (df - median).abs().median()

        return 0.6745 * (df - median) / (mad + 1e-5)

    @classmethod
    def _calculate_iqr(cls, df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
        """
        Расчет интерквартильного
        размаха (IQR)

        Parameters
        ----------
        df : pd.DataFrame
            Данные, для которых необходимо
            определить выбросы

        Returns
        -------
        tuple[pd.Series, pd.Series]
            Нижняя и верхняя границы для выбросов
        """
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
        """
        Расчет выбросов с использованием
        Isolation Forest

        Parameters
        ----------
        df : pd.DataFrame
            Данные, для которых необходимо
            определить выбросы
        contamination : float, optional
            Процент выбросов в данных (по умолчанию 0.1)
        seed : int, optional
            Сид генератора случайных чисел (по умолчанию 14)

        Returns
        -------
        list[int]
            Список с метками выбросов (1 — выброс, 0 — нет)
        """
        # Получение модели Isolation Forest
        model = IsolationForest(contamination=contamination, random_state=seed)
        # Обучение модели
        model.fit(df)
        # Предсказание выбросов
        outliers = model.predict(df)
        return outliers

    @classmethod
    def z_score(
        cls, df: pd.DataFrame, y_column: str | None = None, threshold: float = 3
    ) -> pd.Series:
        """
        Определение выбросов с
        использованием z-оценки

        Parameters
        ----------
        df : pd.DataFrame
            Данные, в которых нужно искать выбросы
        y_column : str | None, optional
            Столбец для анализа выбросов
            (по умолчанию None, анализируется весь DataFrame)
        threshold : float, optional
            Порог для классификации значения
            как выброса (по умолчанию 3)

        Returns
        -------
        pd.Series
            Серия с метками выбросов
            (1 — выброс, 0 — нет)
        """
        # Вычисление z-оценок
        df_for_outliers = np.abs(cls._calculate_z_score(df))
        # Применение порога
        if y_column is not None:
            df_for_outliers = df_for_outliers[[y_column]]
        return (df_for_outliers > threshold).any(axis=1).astype(int)

    @classmethod
    def modified_z_score(
        cls, df: pd.DataFrame, y_column: str | None = None, threshold: float = 3.5
    ) -> pd.Series:
        """
        Определение выбросов с использованием
        модифицированной z-оценки

        Parameters
        ----------
        df : pd.DataFrame
            Данные для поиска выбросов
        y_column : str | None, optional
            Столбец для поиска выбросов
            (по умолчанию None, анализируется весь DataFrame)
        threshold : float, optional
            Порог для классификации значения
            как выброса (по умолчанию 3.5)

        Returns
        -------
        pd.Series
            Серия с метками выбросов
            (1 — выброс, 0 — нет)
        """
        # Вычисление модифицированных z-оценок
        df_for_outliers = cls._calculate_modified_z_score(df)
        # Применение порога
        if y_column is not None:
            df_for_outliers = df_for_outliers[[y_column]]
        return (df_for_outliers > threshold).any(axis=1).astype(int)

    @classmethod
    def iqr(cls, df: pd.DataFrame, y_column: str | None = None) -> pd.Series:
        """
        Определение выбросов с использованием
        метода межквартильного размаха (IQR)

        Parameters
        ----------
        df : pd.DataFrame
            Данные для поиска выбросов
        y_column : str | None, optional
            Столбец для поиска выбросов
            (по умолчанию None, анализируется весь DataFrame)
        threshold : float, optional
            Порог для классификации значения
            как выброса (по умолчанию 1.5)

        Returns
        -------
        pd.Series
            Серия с метками выбросов
            (1 — выброс, 0 — нет)
        """
        # Поиск выбросов в конкртетной колонке
        if y_column is not None:
            df = df[[y_column]]
        # Вычисление интерквартильного размаха
        lower_bound, upper_bound = cls._calculate_iqr(df)
        return ((df < lower_bound) | (df > upper_bound)).any(axis=1).astype(int)

    @classmethod
    def iso_forest(cls, df: pd.DataFrame, y_column: str | None = None) -> list[int]:
        """
        Определение выбросов с использованием
        Isolation Forest

        Parameters
        ----------
        df : pd.DataFrame
            Данные для поиска выбросов
        contamination : float, optional
            Процент выбросов в данных (по умолчанию 0.1)
        y_column : str | None, optional
            Столбец для поиска выбросов (по умолчанию None)
        seed : int, optional
            Сид генератора случайных чисел (по умолчанию 14)

        Returns
        -------
        pd.Series
            Серия с метками выбросов
            (1 — выброс, 0 — нет)
        """
        # Поиск выбросов в конкртетной колонке
        if y_column is not None:
            df = df[[y_column]]

        # Проверка на наличие NaN
        columns_with_nan = df.columns[df.isna().any()].tolist()
        if len(columns_with_nan) != 0:
            raise NanColumnsException(columns_with_nan)
        # Определение выбросов
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
        Определяет выбросы в данных
        при помощи различных методов

        Parameters
        ----------
        df : pd.DataFrame
            Данные, в которых будет
            производиться поиск выбросов
        method_name : str
            Имя метода, при помощи которого
            будут определены выбросы
        y_column : str | None, optional
            Имя поля, в котором необходимо найти выбросы.
            В случае, если поле не указано, поиск выбросов
            производится во всем DataFrame

        Returns
        -------
        dict[str, list[int]]
            Словарь с именем колонки и данными о выбросах.
            В имени колонки будет содержаться не только имя
            метода для определения выбросов, но и y_column,
            если она имеет значения, отличные от None
        """
        # Определение метода для поиска выбросов
        func = getattr(cls, method_name)
        # Приложение метода (поиск выбросов)
        outliers = func(df, y_column)
        if isinstance(outliers, pd.Series):
            outliers = outliers.to_list()
        # Создание имени колонки для столбца с метками выбросов
        name = f"{method_name}_outliers{f"_{y_column}" if y_column is not None else ""}"
        return {name: outliers}


class CorrBuilder:
    """
    Класс для построения
    таблицы с корреляций

    Attributes
    ----------
    headers : list[str]
        Заголовки таблицы
    """

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
        """
        Создает таблицу с корреляций
        между парами колонок

        Parameters
        ----------
        df : pd.DataFrame
            Исходный DataFrame, для которого
            вычисляются корреляции
        left_columns : list[str]
            Список колонок слева, которые будут
            образовывать пары с колонками справа,
            чтобы определеить корреляцию
        right_columns : list[str]
            Список колонок справа, которые будут
            образовывать пары с колонками слева,
            чтобы определеить корреляцию
        round_value : int, optional
            Число знаков после запятой
            для округления (по умолчанию 2)
        dropna : bool, optional
            Флаг для удаления строк с пропущенными
            значениями (по умолчанию True)

        Returns
        -------
        pd.DataFrame
            DataFrame, содержащий пары колонок,
            их размерность, коэффициент Спирмена и p-value
        """
        result = []
        for left_col in left_columns:
            for right_col in right_columns:
                # Удаление строк с пропущенными значениями, если задано dropna=True
                temp_df = df[[left_col, right_col]]
                if dropna is True:
                    temp_df.dropna(inplace=True)
                n = len(temp_df)
                # Вычисление коэффициента Спирмена и p-value
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
    """
    Класс для определения кластеров в данных
    """

    @classmethod
    def _get_name(cls, method: ClusteringMethod) -> str:
        """
        Генерирует имя для результата кластеризации
        в зависимости от выбранного метода

        Parameters
        ----------
        method : ClusteringMethod
            Метод кластеризации, который используется

        Returns
        -------
        str
            Название для столбца с результатами кластеризации
        """
        return f"{method.value}_clusters"

    @classmethod
    def _data_standardization(cls, df: pd.DataFrame) -> np.ndarray:
        """
        Стандартизирует данные для
        кластеризации с помощью StandardScaler

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame, которые необходимо стандартизировать

        Returns
        -------
        np.ndarray
            Стандартизированные данные
        """
        scaler = StandardScaler()
        df_normalized = scaler.fit_transform(df)
        return df_normalized

    @staticmethod
    def kmeans(df: pd.DataFrame, n_clusters: int, seed: int = 14) -> pd.DataFrame:
        """
        Применяет алгоритм KMeans для кластеризации данных

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame с данными для кластеризации
        n_clusters : int
            Число кластеров, на которые нужно разбить данные
        seed : int, optional
            Начальное значение для генератора
            случайных чисел (по умолчанию 14)

        Returns
        -------
        np.ndarray
            Массив меток кластеров для каждой строки данных
        """
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
        """
        Получает результат кластеризации при
        использованием заданного метода и числа кластеров

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame с данными для кластеризации
        method : ClusteringMethod
            Метод кластеризации, который необходимо применить
        n_clusters : int, optional
            Число кластеров (по умолчанию 3)

        Returns
        -------
        dict[str, int]
            Словарь с результатами кластеризации
        """
        # Получение метода для кластеризации
        func = getattr(cls, method.value)
        # Выполнение кластеризации
        result = func(df=df, n_clusters=n_clusters)
        # Определение имени для результата кластеризации
        name = cls._get_name(method)

        return {name: result.tolist()}


class ORBuilder:
    """
    Класс для построения таблицы с OR и 95% CI

    Attributes
    ----------
    binary_set : set
        Множество бинарных значений
    """

    binary_set = {0, 1}

    def _is_binary(self, sr: pd.Series) -> bool:
        """
        Проверяет, является ли столбец бинарным

        Parameters
        ----------
        sr : pd.Series
            Столбец DataFrame для проверки

        Returns
        -------
        bool
            True, если столбец бинарный
            (содержит только 0 и 1), иначе False
        """
        # Удаление пропущенных значений в pandas Series
        sr = sr.dropna()
        # Получение уникальных значений
        unique_vals = set(sr.unique())

        # Проверка на принадлежность к бинарному множеству
        return unique_vals.issubset(self.binary_set)

    def _to_binary(self, sr: pd.Series) -> pd.Series:
        """
        Преобразует столбец в бинарный, заменяя
        максимальные значения на 1, а минимальные на 0

        Parameters
        ----------
        sr : pd.Series
            Столбец, который необходимо преобразовать

        Returns
        -------
        pd.Series
            Столюец с бинарными значениями
        """
        # Определяем максимальное и минимальное значения
        max_value = sr.max()
        min_value = sr.min()

        # Заменяем максимальные значения на 1, а минимальные на 0
        sr = sr.where(sr != max_value, 1).where(sr != min_value, 0)

        return sr

    def _set_datas(self):
        """
        Разбивает исходный DataFrame на два поднабора
        данных по значениям split_column и подготавливает
        структуру для хранения результатов
        """
        # Создание пустого словаря с разбиением данных
        self.datas = dict()
        # Получение групп по split_column
        for i in range(2):
            split_data = self._df[self._df[self.split_column] == i]

            name = f"{self.split_column} == {i} (N = {len(split_data)})"
            self.datas[name] = split_data
            # Добавление пустого списка для
            # хранения результатов по столбцу группы
            self.result[name] = []

        # Добавление пустого списка для хранения результатов ОШ 95% ДИ
        self.result["ОШ 95% ДИ"] = []

    def _calulate(self):
        """
        Выполняет расчет логистической регрессии
        для всех столбцов и вычисляет OR с
        95% доверительным интервалом
        """
        for col in self._df.columns:
            # Пропускаем целевую колонку, потому что
            # не получится искать значения для самой себя
            if col == self.target_column or col == self.split_column:
                continue
            try:
                current_df = self._df[[col, self.target_column]]
                # Удаление строк с пустыми значениями
                current_df = current_df.dropna()

                # Подготовка данных для логистической регрессии
                X = current_df[col]
                y = current_df[self.target_column]

                # Добавление константы для интерсепта
                X = sm.add_constant(X)

                # Создание модели
                model = sm.Logit(y, X)
                fit_model = model.fit()

                # Формирование результата
                local_result = fit_model.conf_int()
                local_result["OR"] = fit_model.params
                local_result.columns = ["2.5%", "97.5%", "OR"]
                local_result = round(np.exp(local_result), 3)

                # Добавление результата в отчет
                self.result["ОШ 95% ДИ"].append(
                    f"{local_result["OR"][col]} ({local_result["2.5%"][col]}; {local_result["97.5%"][col]})"
                )

            except Exception as e:
                self.result["ОШ 95% ДИ"].append("N/A")
                print(e)

            # Добавление количества строк по отношению к общему числу строк
            for name, dict_data in self.datas.items():
                self.result[name].append(
                    f"{len(dict_data[col].dropna())}/{len(dict_data)}"
                )
            self.add_rows.append(col)

    def __init__(self, df: pd.DataFrame, target_column: str, split_column: str):
        """
        Инициализирует объект для
        расчета и подготовки результатов

        Parameters
        ----------
        df : pd.DataFrame
            Исходный DataFrame для расчета
        target_column : str
            Целевая колонка для анализа
        split_column : str
            Колонка для разделения данных на группы
        """
        self._df = df
        self.target_column = target_column
        self.split_column = split_column

    def build(self) -> dict[str, list[str]]:
        """
        Создает таблицу с расчетом OR и 95% CI

        Returns
        -------
        dict[str, list[str]]
            Словарь с результатом
        """
        # Строки с именами столбцов
        self.add_rows = []
        self.result = {"Колонки": self.add_rows}

        # Подготовка данных
        self._set_datas()

        # Проверка на бинарность
        error_columns = []
        for column in (self.target_column, self.split_column):
            if not self._is_binary(self._df[column]):
                error_columns.append(column)

        if len(error_columns) != 0:
            raise BinaryColumnsException(columns=error_columns)

        # Выполнение расчета
        self._calulate()

        return self.result
