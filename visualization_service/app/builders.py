import pandas as pd
import numpy as np

from app.schemas import CorrelationMethod


class CorrelationBuilder:
    """
    Класс для построения корреляционных матриц
    с использованием различных методов корреляции
    """

    @staticmethod
    def build(
        df: pd.DataFrame,
        method: CorrelationMethod,
        round_value: int = 2,
        replace_nan: bool = False,
    ) -> pd.DataFrame:
        """
        Построение корреляционной матрицы для
        pandas DataFrame с указанным методом корреляции

        Parameters
        ----------
        df : pd.DataFrame
            Данные, на основе которых строится корреляционная матрица
        method : CorrelationMethod
            Метод корреляции, который будет использоваться (например, 'pearson', 'spearman')
        round_value : int, optional
            Количество знаков после запятой для округления значений (по умолчанию 2)
        replace_nan : bool, optional
            Флаг для замены значений NaN на None (по умолчанию False)

        Returns
        -------
        pd.DataFrame
            Корреляционная матрица, округленная до заданного
            количества знаков и с возможной заменой NaN значений
        """
        # Построение корреляционной матрицы с указанным методом и округление значений
        result = round(df.corr(method=method.value), round_value)

        # Если требуется, заменяем все NaN значения на None
        if replace_nan is True:
            result = result.replace(np.nan, None)

        return result
