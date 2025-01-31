import os
import time
import json
import requests  # usado para exceções, mas as requisições são via cloudscraper
import cloudscraper
from bs4 import BeautifulSoup
from pathlib import Path
from random import choice

# ---------------------------------------------
# 1) Função para salvar dados em arquivo JSON
# ---------------------------------------------
def write_json(data, filename="teste", directory="."):
    """Salva dados em arquivo JSON, criando pasta se necessário."""
    dir_json = Path(directory)
    if not os.path.exists(dir_json):
        os.makedirs(dir_json)
    with open(dir_json / f"{filename}.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

# ---------------------------------------------
# 2) Função para extrair informações específicas da página
# ---------------------------------------------
def extrair_informacoes(soup):
    """
    Extrai dados específicos de uma reclamação do ReclameAqui (iFood)
    a partir de um objeto BeautifulSoup.
    """
    # A) Título (h1 com class="sc-lzlu7c-3 hnjYTW")
    title_element = soup.find("h1", class_="sc-lzlu7c-3 hnjYTW")
    title = title_element.get_text(strip=True) if title_element else "Sem título"

    # B) Texto da Reclamação (p com class="sc-lzlu7c-17 fRVYjv")
    complaint_element = soup.find("p", class_="sc-lzlu7c-17 fRVYjv")
    complaint_text = complaint_element.get_text(strip=True) if complaint_element else "Sem descrição"

    # C) Localização (div com class="sc-1s8uljb-0 iQmehD")
    location_element = soup.find("div", class_="sc-1s8uljb-0 iQmehD")
    location = location_element.get_text(strip=True) if location_element else "Sem localização"

    # D) Verificar se foi respondida ou não (span com class="sc-1a60wwz-1 zBBWP")
    answered_element = soup.find("span", class_="sc-1a60wwz-1 zBBWP")
    answered_status = answered_element.get_text(strip=True) if answered_element else "Status desconhecido"

    # E) Resposta da empresa (p com class="sc-1o3atjt-4 kWLZRB"), se houver
    response_element = soup.find("p", class_="sc-1o3atjt-4 kWLZRB")
    company_response = response_element.get_text(strip=True) if response_element else "Sem resposta da empresa"

    # F) Informações Detalhadas (div com class="sc-1dmxdqs-0 bceage")
    container_element = soup.find("div", class_="sc-1dmxdqs-0 bceage")
    detailed_info = container_element.get_text(separator=" ", strip=True) if container_element else "Sem informações detalhadas"

    # Monta e retorna um dicionário com os dados extraídos
    scraped_data = {
        "title": title,
        "complaint_text": complaint_text,
        "location": location,
        "answered_status": answered_status,
        "company_response": company_response,
        "detailed_info": detailed_info
    }
    return scraped_data

# ---------------------------------------------
# 3) Configuração do scraper (Cloudflare)
# ---------------------------------------------
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)

# ---------------------------------------------
# 4) Headers para a API
# ---------------------------------------------
API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.reclameaqui.com.br/",
    "Origin": "https://www.reclameaqui.com.br",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Upgrade-Insecure-Requests": "1"
}

# ---------------------------------------------
# 5) Função para coletar JSON da API
# ---------------------------------------------
def get_json_from_api(page: int) -> dict:
    """Faz requisição à API (usando 'scraper' para contornar bloqueios)."""
    url_api = (
        f"https://iosearch.reclameaqui.com.br"
        f"/raichu-io-site-search-v1/query/companyComplains/10/{page}"
        f"?company=38653&problemType=0000000000000002"
    )
    print(f"[DEBUG] Requisição para a API: {url_api}")
    response = scraper.get(url_api, headers=API_HEADERS)

    print(f"[DEBUG] API Status code: {response.status_code}")
    if response.status_code != 200:
        print("[DEBUG] Conteúdo parcial da resposta (erro):")
        print(response.text[:500])
        return {}

    try:
        return response.json()
    except json.JSONDecodeError as e:
        print("[DEBUG] Erro ao decodificar JSON da API:", e)
        return {}

# ---------------------------------------------
# 6) Coletar reclamações (listas, etc.)
# ---------------------------------------------
def coletar_reclamacoes_api(qtd_paginas=500):
    """Coleta reclamações do ReclameAqui (iFood) via API em múltiplas páginas."""
    bases = []
    for pagina in range(1, qtd_paginas + 1):
        data_api = get_json_from_api(pagina)
        complains = (
            data_api.get("complainResult", {})
                    .get("complains", {})
                    .get("data", [])
        )
        print(f"[DEBUG] Página {pagina}: {len(complains)} reclamações encontradas.")
        for reclamacao in complains:
            titulo = reclamacao.get("title", "Sem título")
            descricao = reclamacao.get("description", "Sem descrição")
            data_criacao = reclamacao.get("created", "Sem data")
            usuario_estado = reclamacao.get("userState", "Sem estado")
            status = reclamacao.get("status", "Sem status")
            url_ra = reclamacao.get("url", "Sem URL")

            if url_ra == "Sem URL":
                continue  # pular reclamações sem URL

            # Se a API só retorna o slug (ex.: "suporte_vCU4wiSuirP1slWc"), garantir o prefixo /ifood/
            if not url_ra.startswith("/ifood/"):
                url_ra = f"/ifood/{url_ra}"

            bases.append({
                "Título": titulo,
                "Descrição": descricao,
                "Data de Criação": data_criacao,
                "Estado do Usuário": usuario_estado,
                "Status": status,
                "url": url_ra
            })
    return bases

# ---------------------------------------------
# 7) Scraping detalhado de cada reclamação
# ---------------------------------------------
def fazer_scraping_reclamacoes(bases):
    """Faz o scraping detalhado de cada URL de reclamação em 'bases'."""
    # Lista de User-Agents para rotacionar, se desejar
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"
    ]

    valores_scrap = []
    total = len(bases)

    for idx, base_item in enumerate(bases, start=1):
        # Pequeno atraso para evitar bloqueios
        time.sleep(1)

        url_ra = base_item["url"]
        # Formar URL final
        url_scrap = f"https://www.reclameaqui.com.br{url_ra}"
        print(f"\n[DEBUG] [{idx}/{total}] Scraping => {url_scrap}")

        headers_scrap = {
            "User-Agent": choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
            "Connection": "keep-alive",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.reclameaqui.com.br/"
        }

        try:
            response = scraper.get(url_scrap, headers=headers_scrap)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Erro de conexão em {url_scrap}: {e}")
            continue

        print(f"[DEBUG] Status code: {response.status_code}")
        if response.status_code == 200:
            # Se precisar depurar, pode imprimir um pequeno trecho do HTML
            # print("[DEBUG] Trecho do HTML:\n", response.text[:500])

            # Monta o soup e extrai as informações
            soup = BeautifulSoup(response.text, "html.parser")
            dados_extras = extrair_informacoes(soup)

            # Combina dados da API e do scraping
            scrap_item = {
                "url": url_scrap,
                "Título_API": base_item["Título"],
                "Status_API": base_item["Status"],
                "title_scraped": dados_extras["title"],
                "complaint_text": dados_extras["complaint_text"],
                "location": dados_extras["location"],
                "answered_status": dados_extras["answered_status"],
                "company_response": dados_extras["company_response"],
                "detailed_info": dados_extras["detailed_info"]
            }
            valores_scrap.append(scrap_item)
            print(f"[DEBUG] Dados extraídos com sucesso para: {url_scrap}")

        else:
            print(f"[DEBUG] Resposta não OK (HTTP {response.status_code}). Trecho da resposta:")
            print(response.text[:500])

    return valores_scrap

# ---------------------------------------------
# 8) Execução Principal
# ---------------------------------------------
if __name__ == "__main__":
    start_time = time.time()

    print("[INFO] Coletando reclamações via API...")
    bases_coletadas = coletar_reclamacoes_api(qtd_paginas=500)
    print(f"[INFO] Total de reclamações coletadas: {len(bases_coletadas)}")

    # Salva as reclamações obtidas da API
    write_json(bases_coletadas, filename="arquivo_paginas")

    print("[INFO] Iniciando scraping detalhado das reclamações...")
    resultados = fazer_scraping_reclamacoes(bases_coletadas)

    # Salva o resultado final do scraping
    write_json(resultados, filename="scraping")

    end_time = time.time()
    print(f"[INFO] Processo concluído em {end_time - start_time:.2f} segundos.")
