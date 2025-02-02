import cloudscraper
import time

# URL de teste (substitua pela URL desejada)
TEST_URL = "https://www.reclameaqui.com.br/ifood/mal-atendimento_ZHQukOklgY28dz8m"

# Cria um scraper configurado para simular um navegador
scraper = cloudscraper.create_scraper(
    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
)

# Define os cabeçalhos, forçando "Accept-Encoding" para "identity"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Encoding": "identity"  # Força o servidor a não comprimir a resposta
}

print(f"[DEBUG] Acessando URL: {TEST_URL}")
time.sleep(2)  # Pequeno atraso para evitar requisições muito rápidas

response = scraper.get(TEST_URL, headers=headers)
print("Status Code:", response.status_code)

# Salva o HTML retornado em um arquivo para inspeção manual
with open("teste.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("HTML salvo em teste.html")
