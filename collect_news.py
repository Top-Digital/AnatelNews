import os
import logging
from dotenv import load_dotenv
import mongoengine as me
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import requests

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
SHOW_BROWSER = os.getenv('SHOW_BROWSER', 'False').lower() in ('true', '1', 't')
LOG_FILE = os.getenv('LOG_FILE', 'anatel_news.log')
WEBHOOK_URL = os.getenv('WEBHOOK_URL') if os.getenv('WEBHOOK_URL') else "http://localhost:8080/wp-json/wp/v2/posts"
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')
NEWS_URL = os.getenv('NEWS_URL')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')
NEWS_COLLECTION_NOT_POSTED = os.getenv('NEWS_COLLECTION_NOT_POSTED')

# Configurando o log para DEBUG
logging.basicConfig(
    level=logging.DEBUG,  # <-- Define o nível de logging para DEBUG
    filename=LOG_FILE,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Restringir logs de bibliotecas de terceiros (opcional)
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

logging.debug("Iniciando conexão com o MongoDB via mongoengine.")

# Conexão com MongoDB usando mongoengine
me.connect(db=DB_NAME, host=MONGO_URI)
logging.debug("Conexão com MongoDB estabelecida.")

# Configuração do Selenium
options = Options()
if not SHOW_BROWSER:
    print("Modo headless ativado.")
    options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

logging.debug("Configurando o WebDriver remoto para Selenium.")
driver = webdriver.Remote(
    command_executor='http://localhost:4444/wd/hub',
    options=options
)
logging.debug("WebDriver inicializado com sucesso.")

# Definir os modelos MongoDB
from schemas.news_collection import NewsCollection
from schemas.news_collection_not_posted import NewsCollectionNotPosted

def format_html(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        compact_html = ' '.join(str(soup).split())
        return compact_html
    except Exception as e:
        logging.error(f"Error formatting HTML content: {e}")
        return content.strip()


def collect_news_index():
    logging.info("Iniciando coleta de notícias na página principal.")
    logging.debug(f"NEWS_URL: {NEWS_URL}")
    news_list = []
    url = NEWS_URL
    logging.info(f"Acessando URL: {url}")

    driver.get(url)
    logging.debug("Página carregada no browser Selenium.")

    # Tentar clicar no botão para ver as notícias (caso seja necessário)
    try:
        logging.debug("Tentando clicar no botão de overlay para liberar as notícias.")
        driver.find_element(By.CSS_SELECTOR, 'div > header > div.overlay-wrapper.svelte-lizcfv').click()
        logging.debug("Clique no botão realizado com sucesso.")
    except Exception as e:
        logging.error(f"Erro ao clicar no botão: {e}")

    news_elements = driver.find_elements(By.CSS_SELECTOR, '#ultimas-noticias > ul.noticias.listagem-noticias-com-foto > li')
    logging.info(f"Foram encontrados {len(news_elements)} elementos de notícia.")

    for index, news in enumerate(news_elements):
        news_data = {}
        logging.debug(f"Coletando dados da notícia de índice: {index}")
        try:
            news_data['anatel_URL'] = news.find_element(By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('href')
        except Exception as e:
            news_data['anatel_URL'] = ''
            logging.error(f"Erro ao coletar URL no índice {index}: {e}")

        try:
            title_raw = news.find_element(By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('innerHTML')
            news_data['anatel_Titulo'] = format_html(title_raw)
        except Exception as e:
            news_data['anatel_Titulo'] = ''
            logging.error(f"Erro ao coletar título no índice {index}: {e}")

        try:
            subtitle_raw = news.find_element(By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').get_attribute('innerHTML')
            news_data['anatel_SubTitulo'] = format_html(subtitle_raw)
        except Exception as e:
            news_data['anatel_SubTitulo'] = ''
            logging.error(f"Erro ao coletar subtítulo no índice {index}: {e}")

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except Exception as e:
            news_data['anatel_ImagemChamada'] = ''
            logging.error(f"Erro ao coletar imagem no índice {index}: {e}")

        try:
            desc_raw = news.find_element(By.CSS_SELECTOR, 'div.conteudo > span > span.data').get_attribute('innerHTML')
            news_data['anatel_Descricao'] = format_html(desc_raw)
        except Exception as e:
            news_data['anatel_Descricao'] = ''
            logging.error(f"Erro ao coletar descrição no índice {index}: {e}")

        logging.debug(f"Dados coletados até agora: {news_data}")
        news_list.append(news_data)

    logging.debug(f"Coleta de notícias na página principal concluída. Total coletado: {len(news_list)}")
    return news_list

def collect_news_details(news_url):
    logging.info(f"Coletando detalhes da notícia na URL: {news_url}")
    news_details = {}
    try:
        driver.get(news_url)
        logging.debug("Página de detalhes carregada no Selenium.")
    except Exception as e:
        logging.error(f"Erro ao acessar a URL de detalhes: {news_url}. Erro: {e}")
        return news_details  # Retorna vazio, pois não conseguiu acessar

    try:
        news_details['anatel_DataPublicacao'] = driver.find_element(By.CSS_SELECTOR, '#plone-document-byline > span.documentPublished').text.strip()
        logging.debug(f"Data de publicação coletada: {news_details['anatel_DataPublicacao']}")
    except Exception as e:
        news_details['anatel_DataPublicacao'] = ''
        logging.error(f"Erro ao coletar data de publicação para {news_url}: {e}")

    try:
        news_details['anatel_DataAtualizacao'] = driver.find_element(By.CSS_SELECTOR, '#plone-document-byline > span.documentModified').text.strip()
        logging.debug(f"Data de atualização coletada: {news_details['anatel_DataAtualizacao']}")
    except Exception as e:
        news_details['anatel_DataAtualizacao'] = ''
        logging.warning(f"Não foi possível coletar data de atualização para {news_url}: {e}")

    try:
        news_details['anatel_ImagemPrincipal'] = driver.find_element(By.CSS_SELECTOR, '#media > img').get_attribute('src')
        logging.debug(f"Imagem principal coletada: {news_details['anatel_ImagemPrincipal']}")
    except Exception as e:
        news_details['anatel_ImagemPrincipal'] = ''
        logging.error(f"Erro ao coletar imagem principal para {news_url}: {e}")

    try:
        text_raw = driver.find_element(By.CSS_SELECTOR, '#parent-fieldname-text > div').get_attribute('innerHTML')
        news_details['anatel_TextMateria'] = format_html(text_raw)
        logging.debug("Texto da matéria coletado e formatado.")
    except Exception as e:
        news_details['anatel_TextMateria'] = ''
        logging.error(f"Erro ao coletar texto da matéria para {news_url}: {e}")

    try:
        news_details['anatel_Categoria'] = driver.find_element(By.CSS_SELECTOR, '#form-widgets-categoria').text.strip()
        logging.debug(f"Categoria coletada: {news_details['anatel_Categoria']}")
    except Exception as e:
        news_details['anatel_Categoria'] = ''
        logging.error(f"Erro ao coletar categoria para {news_url}: {e}")

    logging.debug(f"Detalhes coletados: {news_details}")
    return news_details

def send_to_wordpress(data):
    logging.info("Enviando dados para o WordPress.")
    url = WEBHOOK_URL
    headers = {'Content-Type': 'application/json', 'X-Webhook-Token': WEBHOOK_TOKEN}
    logging.debug(f"URL do webhook: {url}, Token: {WEBHOOK_TOKEN}")
    try:
        response = requests.post(url, json=data, headers=headers)
        logging.debug(f"Status da resposta do WordPress: {response.status_code} | Conteúdo: {response.text}")
        return response
    except Exception as e:
        logging.error(f"Erro ao enviar dados para o WordPress: {e}")
        # Retornando um objeto de resposta "mockado" para evitar quebra
        class MockResponse:
            def __init__(self):
                self.status_code = 500
                self._json = {}

            def json(self):
                return self._json

        return MockResponse()

def collect_and_post_news():
    logging.info("Iniciando processo de coleta e postagem de notícias.")
    logging.debug("Chamando collect_news_index()")
    news_index = collect_news_index()
    logging.debug(f"Tamanho de news_index: {len(news_index)}")

    required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_DataPublicacao', 'anatel_TextMateria']

    for i, news in enumerate(news_index):
        logging.debug(f"Processando notícia {i+1}/{len(news_index)}: {news}")
        if news['anatel_URL']:
            logging.debug("Chamando collect_news_details() para obter detalhes da notícia.")
            details = collect_news_details(news['anatel_URL'])
            news.update(details)
            logging.debug(f"Notícia após atualizar com detalhes: {news}")

            if all(news.get(field) for field in required_fields):
                logging.debug("Todos os campos obrigatórios estão presentes, verificando se a notícia já existe no banco.")
                existing_news = NewsCollection.objects(anatel_URL=news['anatel_URL']).first()
                if existing_news:
                    logging.debug(f"Notícia já existe no banco. Verificando data de atualização.")
                    if existing_news.anatel_DataAtualizacao != news['anatel_DataAtualizacao']:
                        logging.debug("Atualização detectada. Enviando para o WordPress.")
                        news['wordpress_AtualizacaoDetected'] = True
                        existing_news.update(**news)
                        response = send_to_wordpress(news)

                        if response.status_code == 200:
                            logging.debug("Atualização no WordPress bem-sucedida. Atualizando registro Mongo.")
                            news['wordpress_AtualizacaoDetected'] = False
                            news['wordpress_DataAtualizacao'] = news['anatel_DataAtualizacao']
                            existing_news.update(**news)
                            logging.info(f"Notícia atualizada (Mongo e WP): {news['anatel_URL']}")
                        else:
                            logging.warning(f"Falha na atualização do WordPress. Código: {response.status_code}")
                else:
                    logging.debug("Notícia não existente no banco. Enviando para o WordPress como nova.")
                    response = send_to_wordpress(news)
                    if response.status_code == 200:
                        logging.debug("Postagem no WordPress bem-sucedida. Salvando no Mongo.")
                        try:
                            post_id = response.json().get('post_id')
                        except Exception:
                            post_id = None
                        news['wordpressPostId'] = post_id
                        news['wordpress_DataPublicacao'] = datetime.now().isoformat()
                        NewsCollection(**news).save()
                        logging.info(f"Nova notícia salva no Mongo e publicada no WP: {news['anatel_URL']}")
                    else:
                        logging.warning(f"Falha na postagem do WordPress. Código: {response.status_code}")
            else:
                logging.debug("Campos obrigatórios ausentes. Salvando em NewsCollectionNotPosted.")
                NewsCollectionNotPosted(**news).save()
                logging.info(f"Notícia salva em NOT_POSTED: {news['anatel_URL']}")
        else:
            logging.warning(f"Notícia sem URL no index. Índice: {i}")

if __name__ == '__main__':
    try:
        collect_and_post_news()
    except Exception as e:
        logging.error(f"Erro fatal na execução: {e}")
    finally:
        logging.debug("Encerrando WebDriver.")
        driver.quit()
        logging.debug("WebDriver encerrado com sucesso.")
