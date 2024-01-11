import collections
from nltk.stem import PorterStemmer
import re
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')


class Preprocessor:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.ps = PorterStemmer()

    def get_doc_id(self, doc):
        arr = doc.split("\t")
        return int(arr[0]), arr[1]

    def tokenizer(self, text):
        stop_words = set(stopwords.words('english'))
        ps = PorterStemmer()
        text = text.lower()
        text = text.strip()
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = " ".join(text.split())
        text = re.sub(r'[^\w]', ' ', text)
        tokens = text.split()
        tokens = [w for w in tokens if not w in stop_words]
        tokens = [ps.stem(w) for w in tokens]
        return tokens
