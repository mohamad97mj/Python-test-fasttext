import pandas as pd
import fasttext
import csv
from settings import Settings
from typing import List
from utils import FileUtils, Logger
from preprocessor import Preprocessor
from utils import PandasUtils
from os import path
from enum import Enum


class Model:
    bios_path = path.join(Settings.DIRECTORY.RESOURCE_DIR.value, 'bio.xlsx')
    inappropriate_bios_path = path.join(Settings.DIRECTORY.RESOURCE_DIR.value, 'inappropriate_bios.xlsx')
    bio_train_path = path.join(Settings.DIRECTORY.GENERATED_SRC_DIR.value, 'bio.train')
    bio_test_path = path.join(Settings.DIRECTORY.GENERATED_SRC_DIR.value, 'bio.test')
    model_path = path.join(Settings.DIRECTORY.GENERATED_SRC_DIR.value, 'model_bio.bin')
    predictions_file = path.join(Settings.DIRECTORY.OUTPUTS_DIR.value, 'predictions.csv')

    class ColNames(Enum):
        BIO = 'bio'

    class Label(Enum):
        APPROPRIATE = "appropriate"
        INAPPROPRIATE = "inappropriate"

    def __init__(self, number_of_appropriate_bios_records: int = 2000, number_of_training_records: int = 2115,
                 number_of_test_records: int = 0):

        self.number_of_appropriate_bios_records = number_of_appropriate_bios_records
        self.inappropriate_bios = PandasUtils.select_series(FileUtils.read_excel_file(self.inappropriate_bios_path),
                                                            self.ColNames.BIO.value)
        self.number_of_inappropriate_bios_records = len(self.inappropriate_bios.index)
        self.number_of_all_bios_records = self.number_of_appropriate_bios_records + self.number_of_inappropriate_bios_records
        self.number_of_training_records = number_of_training_records
        self.number_of_test_records = min(self.number_of_all_bios_records - self.number_of_training_records,
                                          number_of_test_records) if number_of_test_records else self.number_of_all_bios_records - self.number_of_training_records
        self.bios = FileUtils.read_excel_file(self.bios_path)
        self.appropriate_bios = PandasUtils.select_series(self.bios.head(self.number_of_appropriate_bios_records),
                                                          self.ColNames.BIO.value)

        self.__generate_training_and_test_series()
        self.model = None
        self.predictions = []

        Logger.info(
            "Number of appropriate labeled bios records is : {}".format(self.number_of_appropriate_bios_records))
        Logger.info(
            "Number of inappropriate labeled bios records is : {}".format(self.number_of_inappropriate_bios_records))
        Logger.info("Number of training_records is : {}".format(self.number_of_training_records))
        Logger.info("Number of test records is : {}".format(self.number_of_test_records))

    def __preprocess_appropriate_bios(self):
        self.appropriate_bios = PandasUtils.apply_function2series(self.appropriate_bios, Preprocessor.preprocess)
        self.__add_appropriate_label()

    def __preprocess_inappropriate_bios(self):
        self.inappropriate_bios = PandasUtils.apply_function2series(self.inappropriate_bios, Preprocessor.preprocess)
        self.__add_inappropriate_label()

    def __preprocess_bios(self):
        Logger.info("Preprocessing bios ...")
        self.__preprocess_appropriate_bios()
        self.__preprocess_inappropriate_bios()

    @staticmethod
    def __add_label2dataframe(df: pd.DataFrame, col_name: str, label: str) -> pd.DataFrame:
        df[col_name] = '__label__{} '.format(label) + df[col_name].astype(str)

    @staticmethod
    def __add_label2series(series: pd.Series, label: str) -> pd.Series:
        lst = series.tolist()
        return pd.Series(['__label__{} '.format(label) + i for i in lst])

    @staticmethod
    def __add_label(text: str, label: str) -> str:
        return '__label__{} '.format(label) + text

    def __add_appropriate_label(self):
        self.appropriate_bios = self.__add_label2series(self.appropriate_bios, self.Label.APPROPRIATE.value)

    def __add_inappropriate_label(self):
        self.inappropriate_bios = self.__add_label2series(self.inappropriate_bios, self.Label.INAPPROPRIATE.value)

    @staticmethod
    def __remove_labels(ser: pd.Series, prefixes: List) -> pd.Series:
        for prefix in prefixes:
            ser = ser.astype(str).str.lstrip(prefix)
        return ser

    def __extract_assigned_labels_from_test_series(self):
        return [self.Label.APPROPRIATE.value if _.startswith(
            '__label__{}'.format(self.Label.APPROPRIATE.value)) else self.Label.INAPPROPRIATE.value for _ in
                self.test_series]

    def __generate_training_and_test_series(self):
        Logger.info("Generating training and test datasets ...")
        self.__preprocess_bios()
        concatenated = PandasUtils.concat_series([self.appropriate_bios, self.inappropriate_bios])
        shuffled = PandasUtils.shuffle_series(concatenated)
        self.training_series = shuffled.head(self.number_of_training_records)
        self.test_series = shuffled.tail(self.number_of_test_records)
        FileUtils.write_series2file(self.bio_train_path, self.training_series)
        FileUtils.write_series2file(self.bio_test_path, self.test_series)
        self.test_list = self.test_series.to_list()
        self.cleaned_test_list = self.__remove_labels(self.test_series,
                                                      ['__label__{}'.format(l.value) for l in self.Label]).tolist()

    def train_supervised(self, auto=False, save=False, duration=120):
        Logger.info("Training model ...")
        if auto:
            self.model = fasttext.train_supervised(
                input=self.bio_train_path,
                autotuneValidationFile=self.bio_test_path,
                autotuneDuration=duration
            )
        else:
            self.model = fasttext.train_supervised(input=self.bio_train_path)

        if save:
            self.model.save_model(self.model_path)

    def load_model(self):
        Logger.info("Loading model ...")
        self.model = fasttext.load_model(self.model_path)

    def test(self):
        Logger.info("Testing model ...")
        Logger.info(self.model.test(self.bio_test_path))

    def my_predict(self, bio: str):
        Logger.info("Predicting using model ...")
        prediction = self.model.predict(bio)
        predicted_label = self.Label.APPROPRIATE.value if prediction[0][0] == '__label__{}'.format(
            self.Label.APPROPRIATE.value) else self.Label.INAPPROPRIATE.value
        formatted_prediction = {
            'predicted_label': predicted_label,
            'probability': prediction[1][0]
        }
        return formatted_prediction

    def predict_all(self):
        Logger.info("Predicting all using model ...")
        labels = self.__extract_assigned_labels_from_test_series()
        for i in range(self.number_of_test_records):
            prediction = self.model.predict(self.cleaned_test_list[i])
            predicted_label = self.Label.APPROPRIATE.value if prediction[0][0] == '__label__{}'.format(
                self.Label.APPROPRIATE.value) else self.Label.INAPPROPRIATE.value
            self.predictions.append(
                {
                    'bio': self.cleaned_test_list[i],
                    'label': labels[i],
                    'predicted_label': predicted_label,
                    'probability': prediction[1][0]
                })

    def save_results(self):
        Logger.info("Saving results ...")
        with open(self.predictions_file, mode='w', encoding='utf-8') as csv_file:
            fieldnames = ['bio', 'label', 'predicted_label', 'probability']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for p in self.predictions:
                writer.writerow(p)
