import pandas as pd
import numpy as np


from app.schemas import CorrelationMethod


class CorrelationBuilder:
    @staticmethod
    def build(
        df: pd.DataFrame,
        method: CorrelationMethod,
        round_value: int = 2,
        replace_nan: bool = False,
    ) -> pd.DataFrame:
        result = round(df.corr(method=method.value), round_value)

        if replace_nan is True:
            result = result.replace(np.nan, None)

        return result
