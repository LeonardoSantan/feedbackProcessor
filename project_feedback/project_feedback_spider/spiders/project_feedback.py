import scrapy

class MeuSpider(scrapy.Spider):
    name = "project_feedback_spider"
    start_urls = [
        'https://www.reclameaqui.com.br/empresa/ifood/lista-reclamacoes/?pagina=1&problema=0000000000000002'
    ]

    def parse(self, response):
        textos = response.css('.sc-1pe7b5t-0 eJgBOc::text').getall()
        for texto in textos:
            yield {'conteudo': texto}

        # Seguir links para outras páginas, se necessário
        for proximo in response.css('a.next::attr(href)'):
            yield response.follow(proximo, self.parse)

def main():
    parse()


if __name__ == "__main__":
    main()