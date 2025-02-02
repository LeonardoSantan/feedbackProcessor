# teste_modelo.py
import joblib
# Importe também a função se for necessário (caso o pipeline precise dela para aplicar o pré-processamento)
from utils import preprocess_text

# Carrega o modelo salvo
modelo = joblib.load('modelo_classificacao_final.pkl')

# Use o modelo para classificar uma nova reclamação
nova_reclamacao = "O app não está aceitando meu cartão de crédito."
categoria = modelo.predict([nova_reclamacao])
print("Categoria:", categoria[0])
