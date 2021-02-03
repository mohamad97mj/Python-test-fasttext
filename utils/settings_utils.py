import warnings
import pandas as pd


class SettingsUtils:

    @staticmethod
    def config_warning_settings():
        warnings.simplefilter(action='ignore', category=FutureWarning)

    @staticmethod
    def config_dataframe_settings():
        pd.options.mode.chained_assignment = None  # default='warn'
