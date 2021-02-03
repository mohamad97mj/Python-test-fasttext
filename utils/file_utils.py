import pandas as pd
import numpy as np
import json
from typing import List


class FileUtils:
    default_encoding = 'utf-8'

    @staticmethod
    def read_csv_file(file_path: str) -> pd.DataFrame:
        return pd.read_csv(file_path)

    @staticmethod
    def read_json_file(file_path: str, encoding: str = default_encoding):
        with open(file_path, encoding=encoding) as f:
            data = json.load(f)
        return data

    @staticmethod
    def read_excel_file(file_path: str, encoding: str = default_encoding):
        dfs = pd.read_excel(file_path, header=0)
        return dfs

    @staticmethod
    def write_list2file(file_path: str, lst: List, encoding: str = default_encoding):
        with open(file_path, 'w+', encoding=encoding) as f:
            f.write('\n'.join(lst) + '\n')

    @staticmethod
    def write_series2file(file_path: str, series: pd.Series, fmt: str = '%s', encoding: str = default_encoding) -> None:
        np.savetxt(file_path, series.values, fmt=fmt, encoding=encoding)
