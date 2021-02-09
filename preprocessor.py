import re
from hazm import Normalizer, Stemmer, Lemmatizer, stopwords_list, WordTokenizer
from typing import List
import emoji


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
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u'\U00010000-\U0010ffff'
                                   u"\u200d"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\u3030"
                                   u"\ufe0f"
                                   "]+", flags=re.UNICODE)

        first_cleaned_text = emoji_pattern.sub(r'', text)  # no emoji
        return emoji.get_emoji_regexp().sub(r'', first_cleaned_text)

    @staticmethod
    def __remove_punctuation(text: str):
        try:
            return re.sub(r'[\.\?\!\,\:\;\،\(\)\؛\#\%\^\&\$\~\'\"\×\-\_\*\>\<\+\=\\\/]', '', text)
        except TypeError as e:
            print(e, text)

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
        cleaned_text = Preprocessor.remove_noise(str(text))
        normalized_text = Preprocessor.normalize(cleaned_text)
        tokens = Preprocessor.tokenize(normalized_text)
        none_stop_words = Preprocessor.remove_stop_words(tokens)
        # stems = [Preprocessor.stem(w) for w in tokens]
        lemmatized = [Preprocessor.lemmatize(w) for w in none_stop_words]
        return ' '.join(lemmatized)
