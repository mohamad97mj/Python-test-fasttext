import pandas as pd
import fasttext
import csv
from typing import List
from utils import FileUtils
from preprocessor import Preprocessor
from utils import PandasUtils
from os import path
from enum import Enum


class BioModel:
    resource_dir = 'resources/'
    outputs_dir = 'outputs/'
    generate_src_dir = 'generated_src/'
    bios_path = path.join(resource_dir, 'bio.xlsx')
    inappropriate_bios_path = path.join(resource_dir, 'inappropriate_bios.xlsx')
    bio_train_path = path.join(generate_src_dir, 'bio.train')
    bio_test_path = path.join(generate_src_dir, 'bio.test')
    model_path = path.join(generate_src_dir, 'model_bio.bin')
    predictions_file = path.join(outputs_dir, 'predictions.csv')

    class ColNames(Enum):
        BIO = 'bio'

    class Label(Enum):
        APPROPRIATE = "appropriate"
        INAPPROPRIATE = "inappropriate"

    def __init__(self, number_of_appropriate_bios_records: int = 2000, number_of_training_records: int = 2115,
                 number_of_test_records: int = 0):
        self.number_of_appropriate_bios_records = number_of_appropriate_bios_records
        self.inappropriate_bios = FileUtils.read_excel_file(self.inappropriate_bios_path)
        self.number_of_inappropriate_bios_records = len(self.inappropriate_bios.index)
        self.number_of_all_bios_records = self.number_of_appropriate_bios_records + self.number_of_inappropriate_bios_records
        self.number_of_training_records = number_of_training_records
        self.number_of_test_records = min(self.number_of_all_bios_records - self.number_of_training_records,
                                          number_of_test_records) if number_of_test_records else self.number_of_all_bios_records - self.number_of_training_records
        self.bios = FileUtils.read_excel_file(self.bios_path)
        self.appropriate_bios = self.bios.head(self.number_of_appropriate_bios_records)

        self.__generate_training_and_test_series()
        self.model = None
        self.predictions = []

    def __preprocess_dataframe(self):
        pass

    def __preprocess_appropriate_bios(self):
        self.__add_appropriate_label_for_bio_column()
        PandasUtils.apply_function2dataframe(self.appropriate_bios, Preprocessor.preprocess, [self.ColNames.BIO, ])

    def __preprocess_inappropriate_bios(self):
        self.__add_inappropriate_label_for_bio_column()
        PandasUtils.apply_function2dataframe(self.inappropriate_bios, Preprocessor.preprocess, [self.ColNames.BIO, ])

    def __preprocess_bios(self):
        self.__preprocess_appropriate_bios()
        self.__preprocess_inappropriate_bios()

    @staticmethod
    def __add_label(df: pd.DataFrame, col_name: str, label: str) -> pd.DataFrame:
        df[col_name] = '__label__{} '.format(label) + df[col_name].astype(str)

    def __add_appropriate_label_for_bio_column(self) -> pd.DataFrame:
        self.__add_label(self.appropriate_bios, self.ColNames.BIO.value, self.Label.APPROPRIATE.value)

    def __add_inappropriate_label_for_bio_column(self) -> pd.DataFrame:
        self.__add_label(self.inappropriate_bios, self.ColNames.BIO.value, self.Label.INAPPROPRIATE.value)

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
        self.__preprocess_bios()
        selected_inappropriate = PandasUtils.select_series(self.inappropriate_bios, self.ColNames.BIO.value)
        selected_appropriate = PandasUtils.select_series(self.appropriate_bios, self.ColNames.BIO.value)
        concatenated = PandasUtils.concat_series([selected_appropriate, selected_inappropriate])
        shuffled = PandasUtils.shuffle_series(concatenated)
        self.training_series = shuffled.head(self.number_of_training_records)
        self.test_series = shuffled.tail(self.number_of_test_records)
        FileUtils.write_series2file(self.bio_train_path, self.training_series)
        FileUtils.write_series2file(self.bio_test_path, self.test_series)
        self.test_list = self.test_series.to_list()
        self.cleaned_test_list = self.__remove_labels(self.test_series,
                                                      ['__label__{}'.format(l.value) for l in self.Label]).tolist()

    def train_supervised(self, auto=False, save=False):
        if auto:
            self.model = fasttext.train_supervised(
                input=self.bio_train_path,
                autotuneValidationFile=self.bio_test_path,
                autotuneDuration=120
            )
        else:
            self.model = fasttext.train_supervised(input=self.bio_train_path)

        if save:
            self.model.save_model(self.model_path)

    def load_model(self):
        self.model = fasttext.load_model(self.model_path)

    def test(self):
        print(self.model.test(self.bio_test_path))

    def predict_all(self):
        labels = self.__extract_assigned_labels_from_test_series()
        for i in range(self.number_of_test_records):
            prediction = self.model.predict(self.test_list[i])
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
        with open(self.predictions_file, mode='w', encoding='utf-8') as csv_file:
            fieldnames = ['bio', 'label', 'predicted_label', 'probability']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for p in self.predictions:
                writer.writerow(p)

