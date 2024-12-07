import pandas as pd

from typing import Counter

from app.exceptions import ColumnsNotFoundException
from app.exceptions import ColumnsDuplicateException


class ValidateData:
    """
    Класс для валидации данных, связанных с DataFrame
    """

    @staticmethod
    def check_columns(df: pd.DataFrame, columns: list[str] | None) -> pd.DataFrame:
        """
        Проверяет наличие колонок в DataFrame и возвращает его с выбранными колонками

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame, в котором нужно проверить наличие колонок

        columns : list[str] | None
            Список колонок, которые должны быть в DataFrame. Если None, то проверка
            не выполняется и возвращается DataFrame без изменений, то есть со всеми колонками

        Returns
        -------
        pd.DataFrame
            DataFrame с выбранными колонками или без изменений

        Raises
        ------
        ColumnsNotFoundException
            Если в DataFrame отсутствуют указанные колонки, выбрасывается исключение
        """
        if columns:
            # Нахождение колонок, которых нет в DataFrame
            error_columns = set(columns) - set(df.columns)
            if len(error_columns) == 0:
                # Если все колонки найдены - перезаписать DataFrame с этими колонками
                df = df[columns]
            else:
                # Если какие-то колонки не найдены - выбросить исключение
                raise ColumnsNotFoundException(columns=list(error_columns))
        return df


class CorrelationValidation:
    """
    Класс для валидации данных, связанных с корреляцией
    """

    @staticmethod
    def validate(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """
        Проверяет список колонок на дубликаты и проверяет их наличие в DataFrame

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame, с которым будет выполняться проверка

        columns : list[str]
            Список колонок, которые должны быть в DataFrame

        Returns
        -------
        pd.DataFrame
            Преобразованный DataFrame, если все колонки уникальны и присутствуют

        Raises
        ------
        ColumnsDuplicateException
            Если в списке колонок есть дубликаты, выбрасывается исключение

        ColumnsNotFoundException
            Если какие-то колонки отсутствуют в DataFrame, выбрасывается исключение
        """
        # Проверка на дублирующиеся колонки
        column_count = Counter(columns)
        columns_set = set(filter(lambda col: column_count[col] > 1, column_count))
        if len(columns_set) > 1:
            # Если есть дубликаты, рейсится исключение
            raise ColumnsDuplicateException(columns=columns_set)

        # Проверка наличия колонок в DataFrame
        df = ValidateData.check_columns(df=df, columns=columns)

        return df
