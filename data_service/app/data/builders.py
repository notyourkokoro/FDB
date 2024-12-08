import pandas as pd

from sklearn.impute import KNNImputer

from app.exceptions import ColumnsNotFoundException
from app.statistic.exceptions import (
    BadGroupParamsException,
    BadOperationException,
)


class DataBuilder:
    """
    Класс для создания групп данных
    """

    operations = {">", "<", ">=", "<=", "==", "!="}

    @classmethod
    def _get_value(cls, value: str) -> str | float | int:
        """
        Преобразует строковое значение в соответствующий тип
        (строка, число или целое число)

        Parameters
        ----------
        value : str
            Строковое значение, которое необходимо преобразовать

        Returns
        -------
        str | float | int
            Преобразованное значение в соответствующий тип данных
        """
        if value.isdigit():
            return int(value)

        if value.replace(".", "", 1).isdigit():
            return float(value)

        return value

    @classmethod
    def create_group(
        cls, df: pd.DataFrame, params: dict[str, str | int]
    ) -> tuple[str, pd.DataFrame]:
        """
        Создает группу данных на основе заданных параметров

        Parameters
        ----------
        df : pd.DataFrame
            Исходный DataFrame, который нужно разделить на группы
        params : dict[str, str | int]
            Параметры для фильтрации: колонка, операция и значение

        Returns
        -------
        tuple[str, pd.DataFrame]
            Имя группы и соответствующий ей DataFrame

        Raises
        ------
        BadGroupParamsException
            Если количество параметров не равно 3
        ColumnsNotFoundException
            Если указанная колонка не найдена в DataFrame
        BadOperationException
            Если указанная операция неверна
        """
        # Проверка количества параметров
        if len(params) != 3:
            raise BadGroupParamsException

        # Извлечение колонки, операции и значения
        column, operation, value = params.values()
        value = cls._get_value(value)

        # Проверка наличия колонки в DataFrame
        if column not in df.columns:
            raise ColumnsNotFoundException([column])

        # Проверка операции на корректность
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
        """
        Создает несколько групп данных, используя
        заданные параметры для группировки

        Parameters
        ----------
        df : pd.DataFrame
            Исходный DataFrame для обработки
        groups : list[dict[str, str | int]] | None
            Список параметров группировки, если они есть

        Returns
        -------
        dict[str, pd.DataFrame]
            Словарь с именами групп и соответствующими им DataFrame
        """
        # Всегда есть группа с полным DataFrame
        datas = {"all": df}

        if groups is not None:
            for group in groups:
                name, data = cls.create_group(df, group)
                datas[name] = data

        return datas


class RecoveryDataBuilder:
    """
    Класс для восстановления данных
    """

    @classmethod
    def knn(cls, df: pd.DataFrame, **kwargs) -> pd.DataFrame:
        """
        Восстанавливает пропущенные значения в
        данных с использованием KNN-импутации

        Parameters
        ----------
        df : pd.DataFrame
            Данные с пропущенными значениями
        n_neighbors : int, optional
            Количество соседей для использования в KNN (по умолчанию 5)

        Returns
        -------
        pd.DataFrame
            DataFrame с восстановленными значениями
        """
        if kwargs.get("n_neighbors") is None:
            n_neighbors = 5
        else:
            n_neighbors = kwargs["n_neighbors"]

        # Обработка пропущенных значений
        imputer = KNNImputer(n_neighbors=n_neighbors)
        imputer.set_output(transform="pandas")
        result = imputer.fit_transform(df)
        # Преобразование типов к изначальному виду
        result = result.astype(df.dtypes)
        return result

    @classmethod
    def recovery(cls, df: pd.DataFrame, method_name: str, **kwargs) -> pd.DataFrame:
        """
        Восстанавливает данные с использованием указанного метода

        Parameters
        ----------
        df : pd.DataFrame
            Данные с пропущенными значениями
        method_name : str
            Наименование метода для восстановления
        kwargs : dict
            Дополнительные параметры для конкретного метода

        Returns
        -------
        pd.DataFrame
            DataFrame с восстановленными данными
        """
        # Получение метода для восстановления данных
        func = getattr(cls, method_name)
        # Восстановление данных
        result = func(df, **kwargs)
        return result
