from utils import SettingsUtils
from enum import Enum
import os


class Settings:
    class DIRECTORY(Enum):
        RESOURCE_DIR = 'resources/'
        OUTPUTS_DIR = 'outputs/'
        GENERATED_SRC_DIR = 'generated_src/'

    @staticmethod
    def config_settings():
        Settings.__create_required_dirs()
        SettingsUtils.config_warning_settings()
        SettingsUtils.config_dataframe_settings()

    @staticmethod
    def __create_required_dirs():
        for directory in Settings.DIRECTORY:

            if not os.path.exists(directory.value):
                try:
                    os.makedirs(directory.value)
                except OSError as e:
                    print(e)
