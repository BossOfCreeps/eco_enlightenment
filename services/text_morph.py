from nltk import SnowballStemmer, download, word_tokenize
from pymorphy3 import MorphAnalyzer

download("punkt_tab")

morph = MorphAnalyzer()

stemmer = SnowballStemmer("russian")


def parse_text(text: str) -> set[str]:
    cleared_text = {
        word for word in text.lower().split() if morph.parse(word)[0].tag.POS not in ["PREP", "CONJ", "PRCL", "INTJ"]
    }

    lemmatized_words = {stemmer.stem(word) for word in word_tokenize(" ".join(cleared_text))}

    result = lemmatized_words - {",", ".", "!", "?", ";", ":", "...", "-", "+", "(", ")", "[", "]", "—"}

    return result
