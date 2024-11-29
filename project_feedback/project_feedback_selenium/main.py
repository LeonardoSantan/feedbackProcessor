from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

# Configurar o serviço com logs ativados

# Configurar o Firefox no modo headless
options = Options()
options.headless = True  # Ativar modo headless (sem interface gráfica)

# Inicializar o WebDriver com as opções configuradas
driver = webdriver.Firefox(options=options)
service = Service("/usr/local/bin/geckodriver", log_path="/home/leonardopc/GIT/project_feedback/geckodriver.log")

# Abrir uma página
driver.get("https://www.reclameaqui.com.br/empresa/ifood/lista-reclamacoes/?pagina=1&problema=0000000000000002")
print("Título da página:", driver.title)

# Localizar um elemento pela classe e extrair o atributo href
try:
    elemento = driver.find_element(By.CLASS_NAME, "sc-fAGzit")
    print("Atributo href:", elemento.get_attribute("href"))
except Exception as e:
    print("Erro ao encontrar o elemento:", e)

# Fechar o navegador
driver.quit()
