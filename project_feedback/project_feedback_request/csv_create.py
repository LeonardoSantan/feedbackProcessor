import json
import pandas as pd

# Carregar dados a partir do arquivo JSON e criar DataFrame
with open('scraping.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Combinar título e texto da reclamação
df['texto'] = df['title_scraped'] + ' ' + df['complaint_text']

df[['texto']].to_csv('text_complete.csv', index=False)
print("Arquivo CSV 'supervised_classification_results.csv' gerado com as categorias preditas.")


