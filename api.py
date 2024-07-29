import os
import logging
from flask import Flask, jsonify, request, Blueprint
from dotenv import load_dotenv
import mongoengine as me
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import requests

# Importa os modelos
from schemas.news_collection import NewsCollection
from schemas.news_collection_not_posted import NewsCollectionNotPosted

# Configurações do aplicativo Flask
app = Flask(__name__)
api_bp = Blueprint('api', __name__)
logging.basicConfig(level=logging.INFO)

# Carrega variáveis de ambiente
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
SHOW_BROWSER = os.getenv('SHOW_BROWSER', 'False').lower() in ('true', '1', 't')
LOG_FILE = os.getenv('LOG_FILE', 'anatel_news.log')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')
NEWS_URL = os.getenv('NEWS_URL')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')
NEWS_COLLECTION_NOT_POSTED = os.getenv('NEWS_COLLECTION_NOT_POSTED')

# Configura o log
logging.basicConfig(level=logging.INFO)
logging.getLogger('selenium').setLevel(logging.WARNING)

# Conexão com MongoDB usando mongoengine
me.connect(db=DB_NAME, host=MONGO_URI)

# Configuração do Selenium
options = Options()
if not SHOW_BROWSER:
    options.add_argument('--headless')
driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=options)

def format_html(content):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        compact_html = ' '.join(str(soup).split())
        return compact_html
    except Exception as e:
        logging.error(f"Error formatting HTML content: {e}")
        return content.strip()

def collect_news_index():
    news_list = []
    url = NEWS_URL
    logging.info(f"Accessing URL: {url}")
    driver.get(url)
    news_elements = driver.find_elements(By.CSS_SELECTOR, '#ultimas-noticias > ul.noticias.listagem-noticias-com-foto > li')
    logging.info(f"Found {len(news_elements)} news elements")
    for index, news in enumerate(news_elements):
        news_data = {}
        try:
            news_data['anatel_URL'] = news.find_element(By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('href')
        except Exception as e:
            news_data['anatel_URL'] = ''
            logging.error(f"Error collecting URL at index {index}: {e}")

        try:
            news_data['anatel_Titulo'] = format_html(news.find_element(By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('innerHTML'))
        except Exception as e:
            news_data['anatel_Titulo'] = ''
            logging.error(f"Error collecting title at index {index}: {e}")

        try:
            news_data['anatel_SubTitulo'] = format_html(news.find_element(By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').get_attribute('innerHTML'))
        except Exception as e:
            news_data['anatel_SubTitulo'] = ''
            logging.error(f"Error collecting subtitle at index {index}: {e}")

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except Exception as e:
            news_data['anatel_ImagemChamada'] = ''
            logging.error(f"Error collecting image at index {index}: {e}")

        try:
            news_data['anatel_Descricao'] = format_html(news.find_element(By.CSS_SELECTOR, 'div.conteudo > span > span.data').get_attribute('innerHTML'))
        except Exception as e:
            news_data['anatel_Descricao'] = ''
            logging.error(f"Error collecting description at index {index}: {e}")

        news_list.append(news_data)
    return news_list

def collect_news_details(news_url):
    logging.info(f"Collecting details for URL: {news_url}")
    driver.get(news_url)
    news_details = {}
    try:
        news_details['anatel_DataPublicacao'] = driver.find_element(By.CSS_SELECTOR, '#plone-document-byline > span.documentPublished').text.strip()
    except Exception as e:
        news_details['anatel_DataPublicacao'] = ''
        logging.error(f"Error collecting publication date for URL: {news_url}: {e}")

    try:
        news_details['anatel_DataAtualizacao'] = driver.find_element(By.CSS_SELECTOR, '#plone-document-byline > span.documentModified').text.strip()
    except Exception as e:
        news_details['anatel_DataAtualizacao'] = ''
        logging.warning(f"Warning: Could not collect update date for URL: {news_url}: {e}")

    try:
        news_details['anatel_ImagemPrincipal'] = driver.find_element(By.CSS_SELECTOR, '#media > img').get_attribute('src')
    except Exception as e:
        news_details['anatel_ImagemPrincipal'] = ''
        logging.error(f"Error collecting main image for URL: {news_url}: {e}")

    try:
        news_details['anatel_TextMateria'] = format_html(driver.find_element(By.CSS_SELECTOR, '#parent-fieldname-text > div').get_attribute('innerHTML'))
    except Exception as e:
        news_details['anatel_TextMateria'] = ''
        logging.error(f"Error collecting article text for URL: {news_url}: {e}")

    try:
        news_details['anatel_Categoria'] = driver.find_element(By.CSS_SELECTOR, '#form-widgets-categoria').text.strip()
    except Exception as e:
        news_details['anatel_Categoria'] = ''
        logging.error(f"Error collecting category for URL: {news_url}: {e}")

    return news_details

@api_bp.route('/news/collect', methods=['POST'])
def collect_and_post_news():
    logging.info("Starting news collection")
    news_index = collect_news_index()
    required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_DataPublicacao', 'anatel_TextMateria']

    for news in news_index:
        if news['anatel_URL']:
            details = collect_news_details(news['anatel_URL'])
            news.update(details)
            if all(news.get(field) for field in required_fields):
                existing_news = NewsCollection.objects(anatel_URL=news['anatel_URL']).first()
                if existing_news:
                    if existing_news.anatel_DataAtualizacao != news['anatel_DataAtualizacao']:
                        existing_news.update(**news)
                        response = send_to_wordpress(news)
                        if response.status_code == 200:
                            news['wordpress_AtualizacaoDetected'] = False
                            news['wordpress_DataAtualizacao'] = news['anatel_DataAtualizacao']
                            existing_news.update(**news)
                            logging.info(f"Updated existing news: {news['anatel_URL']}")
                else:
                    response = send_to_wordpress(news)
                    if response.status_code == 200:
                        news['wordpressPostId'] = response.json().get('post_id')
                        news['wordpress_DataPublicacao'] = datetime.now().isoformat()
                        NewsCollection(**news).save()
                        logging.info(f"Saved new news: {news['anatel_URL']}")
            else:
                NewsCollectionNotPosted(**news).save()
                logging.info(f"Saved news to not posted collection: {news['anatel_URL']}")

    return jsonify({'message': 'News collected and posted successfully'}), 200

@app.route('/news/send', methods=['POST'])
def send_news():
    news = NewsCollection.objects()  # Supondo que NewsCollection esteja definida
    for item in news:
        item_dict = item.to_mongo().to_dict()
        item_dict['_id'] = str(item_dict['_id'])  # Converter ObjectId para string
        logging.info(f'Enviando notícia: {item_dict}')  # Adiciona o log de cada item antes de enviar

        try:
            response = send_to_wordpress(item_dict)
            if response.status_code == 200:
                response_json = response.json()
                if 'post_id' in response_json:
                    # Atualiza os campos de controle no MongoDB
                    item.update(
                        set__wordpressPostId=response_json.get('post_id'),
                        set__wordpress_DataPublicacao=datetime.now().isoformat(),
                        set__wordpress_AtualizacaoDetected=False,
                        set__wordpress_DataAtualizacao=item_dict.get('anatel_DataAtualizacao')
                    )
                else:
                    logging.error('post_id não encontrado na resposta do WordPress')
                    return jsonify({'error': 'post_id não encontrado na resposta do WordPress'}), 500
            else:
                logging.error(f'Falha ao enviar notícia: {response.content}')
                return jsonify({'error': 'Failed to send news'}), 500
        except requests.exceptions.RequestException as e:
            logging.error(f'Erro ao enviar notícia: {e}')
            return jsonify({'error': 'Erro ao enviar notícia'}), 500

    return jsonify({'message': 'News sent successfully'}), 200

def send_to_wordpress(data):
    url = WEBHOOK_URL
    headers = {'Content-Type': 'application/json', 'X-Webhook-Token': 'your_token_here'}
    response = requests.post(url, json=data, headers=headers)
    return response

app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)