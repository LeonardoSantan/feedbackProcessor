# utils.py
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer

# Pré-compilação das expressões regulares
regex_pontuacao = re.compile(r'[^\w\s]')
regex_digitos = re.compile(r'\d+')

# Carrega recursos do NLTK
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)
nltk.download('rslp', quiet=True)

# Define variáveis globais para evitar problemas de pickling
STOP_WORDS = set(stopwords.words('portuguese'))
STEMMER = RSLPStemmer()

def preprocess_text(text):
    """
    Converte o texto para minúsculas, remove pontuação e dígitos, realiza tokenização,
    remove stopwords e aplica o stemmer RSLP.
    """
    text = text.lower()
    text = regex_pontuacao.sub('', text)
    text = regex_digitos.sub('', text)
    tokens = word_tokenize(text, language='portuguese')
    tokens = [word for word in tokens if word not in STOP_WORDS]
    tokens = [STEMMER.stem(word) for word in tokens]
    return ' '.join(tokens)
