import pandas as pd

from app.exceptions import ColumnsNotFoundException, NotNumericTypeException


class ValidateData:
    """
    Класс для проверки и валидации данных в DataFrame
    """

    @staticmethod
    def check_columns(df: pd.DataFrame, columns: list[str] | None) -> pd.DataFrame:
        """
        Проверяет наличие указанных колонок в
        DataFrame и возвращает его с выбранными колонками

        Parameters
        ----------
        df : pd.DataFrame
            Данные, которые нужно проверить
        columns : list[str] | None
            Список колонок, которые должны присутствовать в DataFrame.
            Если None, тогда будут выбраны все колонки

        Returns
        -------
        pd.DataFrame
            DataFrame с нужными колонками

        Raises
        ------
        ColumnsNotFoundException
            Если хотя бы одна из указанных
            колонок не найдена в DataFrame
        """
        if columns:
            # Определение колонок, которых нет в DataFrame
            error_columns = set(columns) - set(df.columns)
            if len(error_columns) == 0:
                # Возвращение DataFrame с нужными колонками
                df = df[columns]
            else:
                # Рейсится исключения, если хотя бы одна колонка не найдена
                raise ColumnsNotFoundException(columns=list(error_columns))
        return df

    @staticmethod
    def check_numeric_type(df: pd.DataFrame, columns: list[str]):
        """
        Проверяет, что указанные колонки в DataFrame содержат числовые данные

        Parameters
        ----------
        df : pd.DataFrame
            Данные для проверки
        columns : list[str]
            Список колонок, которые нужно проверить
            на принадлежность к числовому типу

        Raises
        ------
        NotNumericTypeException
            Если хотя бы одна из указанных колонок не содержит числовые данные
        """
        error_columns = []
        for column in columns:
            # Проверка, является ли тип данных в колонке числовым
            if not pd.api.types.is_numeric_dtype(df[column]):
                error_columns.append(column)
        if len(error_columns) != 0:
            # Рейсится исключения для колонок с неверным типом
            raise NotNumericTypeException(columns=error_columns)
