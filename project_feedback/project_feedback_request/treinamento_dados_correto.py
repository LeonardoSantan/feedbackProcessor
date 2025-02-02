import pandas as pd
import re
import nltk
import joblib
import numpy as np

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import RSLPStemmer

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Se a função de pré-processamento estiver em um módulo separado, importe-a:
from utils import preprocess_text

# -----------------------------
# Baixar recursos do NLTK (se necessário)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('rslp')

# -----------------------------
# Carregar o arquivo CSV
# O CSV deve conter pelo menos duas colunas: "texto" e "categoria"
df = pd.read_csv('text_complete_classificado.csv')

print("Amostra dos dados:")
print(df.head())

# -----------------------------
# Exibir a distribuição original das classes
print("\nDistribuição das classes (antes de filtrar):")
print(df['categoria'].value_counts())

# -----------------------------
# Filtrar classes com menos de 2 ocorrências para evitar problemas na estratificação
min_ocorrencias = 2
classes_validas = df['categoria'].value_counts()[df['categoria'].value_counts() >= min_ocorrencias].index
df_filtrado = df[df['categoria'].isin(classes_validas)].copy()

print("\nDistribuição das classes (após filtrar):")
print(df_filtrado['categoria'].value_counts())

# -----------------------------
# Preparar os dados para o treinamento
X = df_filtrado['texto']      # Textos a serem processados
y = df_filtrado['categoria']  # Rótulos (classificação refinada)

# Dividir os dados em treino e teste (80% treino, 20% teste) com estratificação
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -----------------------------
# Criar o pipeline que integra a vetorização e o classificador
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=5000, preprocessor=preprocess_text)),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Treinar o modelo
pipeline.fit(X_train, y_train)

# Fazer previsões no conjunto de teste
y_pred = pipeline.predict(X_test)

# Exibir o relatório de classificação
print("\nRelatório de Classificação:")
print(classification_report(y_test, y_pred, zero_division=0))

# -----------------------------
# Prever a classificação para todos os textos do CSV filtrado
df_filtrado['classificacao_predita'] = pipeline.predict(df_filtrado['texto'])

# Salvar o DataFrame com as previsões em um novo arquivo CSV
df_filtrado.to_csv('resultado_classificacao.csv', index=False)
print("\nArquivo 'resultado_classificacao.csv' gerado com a classificação predita para cada texto.")

# -----------------------------
# Salvar o modelo treinado para uso futuro
joblib.dump(pipeline, 'modelo_classificacao_supervisionada.pkl')
print("Modelo salvo em 'modelo_classificacao_supervisionada.pkl'.")
