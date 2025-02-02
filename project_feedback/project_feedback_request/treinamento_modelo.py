# treinamento_modelo.py
import json
import pandas as pd

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report

# Importe a função de pré-processamento do módulo utils
from utils import preprocess_text

def categorizar_reclamacao(text):
    """
    Atribui uma categoria ao texto com base em palavras-chave.
    Essa função serve para gerar rótulos "ground truth".
    """
    text = text.lower()
    if any(word in text for word in ['app', 'aplicativo', 'crash', 'travando', 'lento', 'atualização']):
        return 'Problemas com App'
    elif any(word in text for word in ['loja', 'restaurante', 'cardápio', 'pedido', 'comida', 'entrega']):
        return 'Problemas com Loja'
    elif any(word in text for word in ['cliente', 'atendimento', 'suporte', 'resposta', 'chamado', 'insatisfeito']):
        return 'Problemas com Cliente'
    elif any(word in text for word in ['financeiro', 'pagamento', 'cartão', 'reembolso', 'dinheiro', 'conta', 'tarifa']):
        return 'Problemas com Financeiro'
    elif any(word in text for word in ['dúvida', 'como funciona', 'pergunta', 'informação', 'ajuda']):
        return 'Dúvidas'
    else:
        return 'Outros'

# -----------------------------
# Carregar dados a partir do arquivo JSON e criar DataFrame
with open('scraping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Combinar título e texto da reclamação
df['texto'] = df['title_scraped'] + ' ' + df['complaint_text']

# Gerar rótulos (categorias) utilizando a função de categorização
df['categoria'] = df['complaint_text'].apply(categorizar_reclamacao)

print("Distribuição das categorias (ground truth):")
print(df['categoria'].value_counts())

# -----------------------------
# Preparar dados e rótulos
X = df['texto']
y = df['categoria']

# Dividir os dados em treino e teste (opcional)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Criar o pipeline com TfidfVectorizer e LogisticRegression
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(max_features=5000, preprocessor=preprocess_text)),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Treinar o modelo
pipeline.fit(X_train, y_train)

# Avaliar o modelo no conjunto de teste (opcional)
y_pred = pipeline.predict(X_test)
print("\nRelatório de Classificação (dados de teste):")
print(classification_report(y_test, y_pred))

# Prever a categoria para todos os textos (ou para novos dados)
df['categoria_predita'] = pipeline.predict(X)

# Salvar os resultados em um arquivo CSV
df[['texto', 'categoria', 'categoria_predita']].to_csv('supervised_classification_results.csv', index=False)
print("Arquivo CSV 'supervised_classification_results.csv' gerado com as categorias preditas.")

# Salvar o modelo treinado para uso futuro (opcional)
joblib.dump(pipeline, 'supervised_classification_model.pkl')
