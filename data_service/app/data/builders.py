import pandas as pd

from sklearn.impute import KNNImputer


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
