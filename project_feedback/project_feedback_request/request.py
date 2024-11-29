import gzip
import http.client
import json
import os
import time
from pathlib import Path
start = time.time()



class request_base:
    conn = http.client.HTTPSConnection("iosearch.reclameaqui.com.br")

    # Cabeçalhos copiados do navegador
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",  # Aceitar compressão
        "Referer": "https://www.reclameaqui.com.br/",
        "Origin": "https://www.reclameaqui.com.br",
        "Connection": "keep-alive",
    }

    def conexao(self, url):
        # Fazer a requisição GET
        self.conn.request("GET", f"{url}", headers=self.headers)
        print(url)
        # Obter a resposta
        response = self.conn.getresponse()
        response_data = {}  # Inicializa a variável para evitar UnboundLocalError
        # Processar a resposta
        if response.status == 200:
            # Verificar se a resposta está comprimida
            if response.getheader("Content-Encoding") == "gzip":
                # Descomprimir a resposta
                decompressed_data = gzip.decompress(response.read())
                # Decodificar o texto
                dados = decompressed_data.decode("utf-8")
            else:
                # Resposta sem compressão
                dados = response.read().decode("utf-8")

            # Decodificar a string JSON em um objeto Python
            try:
                response_data = json.loads(dados)
            except json.JSONDecodeError as e:
                print(f"Erro ao decodificar JSON: {e}")
                response_data = {}
        else:
            print(f"Erro ao acessar a API: {response.status} - {response.reason}")
        return response_data


def write_json(data, filename="teste", directory="."):
    dir_json = Path(directory)
    if not os.path.exists(dir_json):
        os.makedirs(dir_json)
    with open(f"{directory}/{filename}.json", "w", encoding="utf-8") as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

request = request_base()
i=0
bases = []
for paginas in range(509):
    i+=1
    url = f"/raichu-io-site-search-v1/query/companyComplains/10/{i}?company=38653&problemType=0000000000000002"
    response_data = request.conexao(url)
    complains = response_data.get("complainResult", {}).get("complains", {}).get("data", [])

    # Iterar sobre as reclamações e imprimir detalhes relevantes
    for reclamacao in complains:
        titulo = reclamacao.get("title", "Sem título")
        descricao = reclamacao.get("description", "Sem descrição")
        data_criacao = reclamacao.get("created", "Sem data")
        usuario_estado = reclamacao.get("userState", "Sem estado")
        status = reclamacao.get("status", "Sem status")
        url = reclamacao.get("url", "Sem status")
        bases.append({
        "Título": titulo,
        "Descrição": descricao,
        "Data de Criação": data_criacao,
        "Estado do Usuário": usuario_estado,
        "Status": status,
        "url": url
    })
write_json(bases, "arquivo_paginas")
i = 0
tag_class = []
valores_scrap = []
for base in bases:
    i += 1
    url = base["url"]
    resultado = "_".join(url.split("_")[1:])
    url = f"/raichu-io-site-search-v1/companypage-details/linked-faqs/complain/{resultado}"
    response_data = request.conexao(url)
    complains = response_data.get("complainResult", {}).get("complains", {}).get("data", [])

    response_data = request.conexao(url)
    if response_data:
        complains = response_data.get("complainResult", {}).get("complains", {}).get("data", [])
        for reclamacao in complains:
            title = reclamacao.get("title", "Sem título")
            text = reclamacao.get("text", "Sem texto")
            for tag in reclamacao["tagList"]:
                tag_class.append(tag["name"])
                criacao = tag["created"]
            valores_scrap.append({
                "title": title,
                "text": text,
                "tag_class": tag_class,
                "criacao": criacao
            })
write_json(valores_scrap, "scraping")

end = time.time()
print(end - start)
