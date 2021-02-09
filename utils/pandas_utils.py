import pandas as pd
from typing import List, Dict, Callable
from pandas import DataFrame, Series


# A util class for pandas series and data frames
class PandasUtils:

    @staticmethod
    def strip_str_list(lst: List) -> List:
        return list(map(str.strip, lst))

    @staticmethod
    def series_to_list(series: Series) -> List:
        return series.tolist()

    @staticmethod
    def concat_series(list_of_series: List) -> Series:
        return pd.concat(list_of_series)

    @staticmethod
    def shuffle_series(series: Series) -> Series:
        return series.sample(frac=1)

    @staticmethod
    def select_series(df: DataFrame, col_name: str) -> Series:
        return df[col_name]

    @staticmethod
    def dataframe2dict_of_lists(df: DataFrame) -> Dict:
        return df.to_dict('list')

    @staticmethod
    def dict_of_lists2dataframe(dic: Dict) -> DataFrame:
        data_frame = DataFrame({k: Series(v) for k, v in dic.items()})
        return data_frame

    @staticmethod
    def apply_function2dataframe(df: DataFrame, f: Callable, columns: List = None) -> DataFrame:
        columns = columns or df.keys()
        dol = PandasUtils.dataframe2dict_of_lists(df)
        for k, v in dol.items():
            if k in columns:
                dol[k] = [f(i) for i in v]
        return PandasUtils.dict_of_lists2dataframe(dol)

    @staticmethod
    def apply_function2series(series: Series, f: Callable) -> Series:
        lst = series.tolist()
        series = Series([f(i) for i in lst])
        return series
