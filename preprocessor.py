import re
from hazm import Normalizer, Stemmer, Lemmatizer, stopwords_list, WordTokenizer
from typing import List


class Preprocessor:
    normalizer = Normalizer()
    stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    tokenizer = WordTokenizer()
    stop_words = stopwords_list()

    @staticmethod
    def remove_noise(text: str) -> str:
        return Preprocessor.__remove_punctuation(Preprocessor.__remove_emojis(text))

    @staticmethod
    def remove_stop_words(tokens: List) -> str:
        return [t for t in tokens if t not in Preprocessor.stop_words]

    @staticmethod
    def __remove_emojis(text: str):
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)  # no emoji

    @staticmethod
    def __remove_punctuation(text: str):
        return re.sub(r'[\.\?\!\,\:\;\،\(\)\؛\"]', '', text)

    @staticmethod
    def normalize(text: str) -> str:
        return Preprocessor.normalizer.normalize(text)

    @staticmethod
    def stem(word: str) -> str:
        return Preprocessor.stemmer.stem(word)

    @staticmethod
    def lemmatize(word: str) -> str:
        return Preprocessor.lemmatizer.lemmatize(word)

    @staticmethod
    def tokenize(text: str) -> str:
        return Preprocessor.tokenizer.tokenize(text)

    @staticmethod
    def preprocess(text: str) -> str:
        cleaned_text = Preprocessor.remove_noise(text)
        normalized_text = Preprocessor.normalize(cleaned_text)
        tokens = Preprocessor.tokenize(normalized_text)
        none_stop_words = Preprocessor.remove_stop_words(tokens)
        # stems = [Preprocessor.stem(w) for w in tokens]
        lemmatized = [Preprocessor.lemmatize(w) for w in none_stop_words]
        return ' '.join(lemmatized)

