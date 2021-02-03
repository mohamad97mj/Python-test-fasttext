from utils import SettingsUtils


class Settings:

    @staticmethod
    def config_settings():
        SettingsUtils.config_warning_settings()
        SettingsUtils.config_dataframe_settings()
