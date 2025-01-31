import os
import time
import json
import requests  # para tratar exceções
import cloudscraper
from bs4 import BeautifulSoup, builder
from pathlib import Path
from random import choice


# ---------------------------------------------
# 1) Função para salvar dados em arquivo JSON
# ---------------------------------------------
def write_json(data, filename="teste", directory="."):
    """Salva dados em arquivo JSON, criando a pasta se necessário."""
    dir_json = Path(directory)
    if not os.path.exists(dir_json):
        os.makedirs(dir_json)
    with open(dir_json / f"{filename}.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)


# ---------------------------------------------
# 2) Função para extrair informações da reclamação
# ---------------------------------------------
def extrair_informacoes(soup):
    """
    Extrai os dados da reclamação usando os seletores conforme o HTML fornecido.
    """
    # Título
    title_element = soup.find("h1", {"data-testid": "complaint-title"})
    title = title_element.get_text(strip=True) if title_element else "Sem título"

    # Texto da reclamação
    complaint_element = soup.find("p", {"data-testid": "complaint-description"})
    complaint_text = complaint_element.get_text(strip=True) if complaint_element else "Sem descrição"

    # Localização
    location_element = soup.find("span", {"data-testid": "complaint-location"})
    location = location_element.get_text(strip=True) if location_element else "Sem localização"

    # Status (se respondida ou não)
    answered_element = soup.find("span", class_="sc-1a60wwz-1 zBBWP")
    answered_status = answered_element.get_text(strip=True) if answered_element else "Status desconhecido"

    # Resposta da empresa (caso exista)
    response_element = soup.find("p", class_="sc-1o3atjt-4 kWLZRB")
    company_response = response_element.get_text(strip=True) if response_element else "Sem resposta da empresa"

    # Informações detalhadas: extraímos o conteúdo do container principal da reclamação.
    container_element = soup.find("div", {"data-testid": "complaint-content-container"})
    detailed_info = container_element.get_text(" ", strip=True) if container_element else "Sem informações detalhadas"

    return {
        "title": title,
        "complaint_text": complaint_text,
        "location": location,
        "answered_status": answered_status,
        "company_response": company_response,
        "detailed_info": detailed_info
    }


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
# 4) Headers para a API e scraping
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

SCRAPING_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "identity",  # Força o envio do HTML descomprimido
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
    "Connection": "keep-alive",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.reclameaqui.com.br/"
}


# ---------------------------------------------
# 5) Função para coletar JSON via API
# ---------------------------------------------
def get_json_from_api(page: int) -> dict:
    """Faz requisição à API do ReclameAqui (iFood) e retorna o JSON."""
    url_api = (
        f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/query/companyComplains/10/{page}"
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
# 6) Função para coletar reclamações via API
# ---------------------------------------------
def coletar_reclamacoes_api(qtd_paginas=500):
    """Coleta reclamações do ReclameAqui (iFood) via API em múltiplas páginas."""
    bases = []
    for pagina in range(1, qtd_paginas + 1):
        data_api = get_json_from_api(pagina)
        complains = data_api.get("complainResult", {}).get("complains", {}).get("data", [])
        print(f"[DEBUG] Página {pagina}: {len(complains)} reclamações encontradas.")
        for reclamacao in complains:
            titulo = reclamacao.get("title", "Sem título")
            descricao = reclamacao.get("description", "Sem descrição")
            data_criacao = reclamacao.get("created", "Sem data")
            usuario_estado = reclamacao.get("userState", "Sem estado")
            status = reclamacao.get("status", "Sem status")
            url_ra = reclamacao.get("url", "Sem URL")
            if url_ra == "Sem URL":
                continue
            # Se a API retorna apenas o slug (por exemplo, "mal-atendimento_ZHQukOklgY28dz8m"),
            # forçamos o prefixo "/ifood/".
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
# 7) Função para realizar o scraping detalhado
# ---------------------------------------------
def fazer_scraping_reclamacoes(bases):
    """Faz o scraping detalhado de cada reclamação usando os seletores validados."""
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
        time.sleep(1)  # Pequena pausa para evitar bloqueios

        url_ra = base_item["url"]
        url_scrap = f"https://www.reclameaqui.com.br{url_ra}"
        print(f"\n[DEBUG] [{idx}/{total}] Scraping => {url_scrap}")

        headers = SCRAPING_HEADERS.copy()
        headers["User-Agent"] = choice(USER_AGENTS)

        try:
            _scraper = cloudscraper.create_scraper()
            response = _scraper.get(url_scrap, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Erro de conexão em {url_scrap}: {e}")
            continue

        print(f"[DEBUG] Status code: {response.status_code}")
        if response.status_code == 200:
            # Tenta fazer o parsing com html.parser; se der erro, tenta lxml
            try:
                soup = BeautifulSoup(response.text, "html.parser")
            except builder.ParserRejectedMarkup as e1:
                print("[DEBUG] Erro com 'html.parser'. Tentando 'lxml'...")
                try:
                    soup = BeautifulSoup(response.text, "lxml")
                except Exception as e2:
                    print("[DEBUG] Falha também com 'lxml'. Pular este item.")
                    continue

            dados_extras = extrair_informacoes(soup)

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
            print(f"[DEBUG] Resposta HTTP {response.status_code}. Trecho da resposta:")
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

    # Salva os dados brutos da API
    write_json(bases_coletadas, "arquivo_paginas")

    print("[INFO] Iniciando scraping detalhado das reclamações...")
    resultados = fazer_scraping_reclamacoes(bases_coletadas)

    # Salva o resultado final do scraping
    write_json(resultados, "scraping")

    end_time = time.time()
    print(f"[INFO] Processo concluído em {end_time - start_time:.2f} segundos.")
