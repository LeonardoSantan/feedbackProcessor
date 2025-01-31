import time
import cloudscraper

TEST_URL = "https://www.reclameaqui.com.br/ifood/suporte_vCU4wiSuirP1slWc"

scraper = cloudscraper.create_scraper()

def teste_html(url):
    print(f"[DEBUG] Acessando URL: {url}")
    time.sleep(2)
    # Accept-Encoding inclui "br", mas se a lib brotli estiver instalada,
    # o requests descomprime sozinho
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Encoding": "gzip, deflate, br"
    }
    response = scraper.get(url, headers=headers)
    print(f"[DEBUG] Status code: {response.status_code}")

    if response.status_code == 200:
        # Apenas imprime parte do response.text, que já deve estar descomprimido
        print("[DEBUG] Trecho do HTML (primeiros 500 chars):")
        print(response.text[:500])
    else:
        print("[DEBUG] Erro ou status não OK:", response.status_code)
        print(response.text[:500])

if __name__ == "__main__":
    teste_html(TEST_URL)
