import requests

# URL da API
url = "https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/query/companyComplains/10/0"

# Cabeçalhos da requisição
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.5",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Origin": "https://www.reclameaqui.com.br",
    "Referer": "https://www.reclameaqui.com.br/",
    "Pragma": "no-cache",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-site",
    "Sec-GPC": "1",
    "TE": "trailers",
}

# Cookies da requisição
cookies = {
    "_cfuvid": "au0Hu3Bjmxj6THG7RgQrYj0fhKiMurwGqLvcsv2b38Q-1732724069496-0.0.1.1-604800000",
    "_gcl_au": "1.1.261842099.1732724070",
    "_ga_GQ3KZJ0431": "GS1.1.1732729956.3.1.1732730952.56.0.0",
    "_ga": "GA1.1.1489354096.1732724070",
    "__privaci_cookie_consent_uuid": "76250680-7918-43fe-9519-92ce29a883e9:11",
    "__privaci_cookie_consent_generated": "76250680-7918-43fe-9519-92ce29a883e9:11",
    "_vwo_uuid_v2": "DD7B08933C858BEAAF2116278E7823458|dfabeac7a8cc782b062fa4b20f210ff9",
    "_vwo_uuid": "DD7B08933C858BEAAF2116278E7823458",
    "_vwo_ds": "3%3Aa_0%2Ct_0%3A0%241732",
    "_gid": "GA1.3.720677378.1732730771",
    "cf_clearance": "0xpiwaZmexqmq.rJtJ70ubfg0Aa73HmN2LRqS2tjstk-1732730770-1.2.1.1-7eEN3zeUDRdrcxexRawmvDZT94P1P_w7QQorTUYeJ7uVvP29OqHClSe_HCrhN3C6W5SnLkkj6dK3LdJzKKa18kEHutZMW5QqbFQoUv_ZsVObGzHE55.5DNh8J1kOcsyMEo2B_OenGvELvnFcV3nLAUzvgkU_eQ0jG496K_01sf9qWWDVQEwPSwfQXNUpz5V_w1CFDiTpZP4c4d4FjxipE9qGn.3MG5YzSGsZgAIMyZYVSnk_2iwFhDgkwOYnt3Vy42P_Kb0KcjMNo97lbx_OqykhrCaEd5R1eJfaizx60y8PSIdnw15h1yodnh_FXsXv1fXuIvi0m89xVam1rENfig",
}

# Parâmetros da API
params = {
    "company": 38653,  # ID da empresa (iFood neste caso)
    "problemType": "0000000000000002",  # Tipo de problema
}

# Fazer a requisição GET
response = requests.get(url, headers=headers, cookies=cookies, params=params)

# Processar a resposta
if response.status_code == 200:
    # Processar o JSON retornado
    dados = response.json()

    # Iterar sobre as reclamações
    for reclamacao in dados.get("complains", []):
        titulo = reclamacao.get("title", "Sem título")
        descricao = reclamacao.get("description", "Sem descrição")
        data = reclamacao.get("created", "Sem data")
        print(f"Título: {titulo}\nDescrição: {descricao}\nData: {data}\n")
else:
    print(f"Erro ao acessar a API: {response.status_code}")
