# treinamento_modelo.py
import json
import pandas as pd

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

# Importe a função de pré-processamento do módulo utils
from utils import preprocess_text


# -----------------------------
# Carregar dados do arquivo JSON e criar DataFrame
with open('scraping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Combinar título e texto da reclamação
df['texto'] = df['title_scraped'] + ' ' + df['complaint_text']

print("Amostra de textos:")
print(df['texto'].head())

# -----------------------------
# Vetorização dos textos usando TfidfVectorizer
vectorizer = TfidfVectorizer(max_features=5000, preprocessor=preprocess_text)
X_tfidf = vectorizer.fit_transform(df['texto'])

# -----------------------------
# Definir o número de clusters (por exemplo, 5) e treinar o modelo KMeans
n_clusters = 5  # Você pode ajustar esse número ou determinar com métodos como o Elbow Method
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(X_tfidf)

# Atribuir os clusters aos textos
df['cluster'] = kmeans.labels_
print("\nDistribuição dos clusters:")
print(df['cluster'].value_counts())

# Salvar os resultados (texto e cluster) em um arquivo CSV
df[['texto', 'cluster']].to_csv('unsupervised_clustering_results.csv', index=False)
print("Arquivo CSV 'unsupervised_clustering_results.csv' gerado com as atribuições de clusters.")

# Salvar o vectorizer e o modelo KMeans para uso futuro (opcional)
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
joblib.dump(kmeans, 'kmeans_clustering_model.pkl')
