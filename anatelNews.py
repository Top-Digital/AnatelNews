import os
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')
NEWS_COLLECTION_NOT_POSTED = os.getenv('NEWS_COLLECTION_NOT_POSTED')
SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'
LOG_FILE = os.getenv('LOG_FILE')

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db[NEWS_COLLECTION]
news_collection_not_posted = db[NEWS_COLLECTION_NOT_POSTED]

# drop collections
news_collection.drop()
news_collection_not_posted.drop()

# Selenium setup
options = Options()
if not SHOW_BROWSER:
    options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(
    '/usr/local/bin/chromedriver'), options=options)


def format_html(content):
    return ''.join(BeautifulSoup(content, 'html.parser').stripped_strings)


def collect_news_index():
    url = "https://www.gov.br/anatel/pt-br/assuntos/noticias"
    driver.get(url)
    news_list = []
    news_elements = driver.find_elements(
        By.CSS_SELECTOR, '#ultimas-noticias > ul.noticias.listagem-noticias-com-foto > li')

    for index, news in enumerate(news_elements):
        news_data = {}
        try:
            news_data['anatel_URL'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('href')
        except:
            news_data['anatel_URL'] = ''
            logging.error(f"Error collecting URL at index {index}")

        try:
            news_data['anatel_Titulo'] = format_html(news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('innerHTML'))
        except Exception as e:
            news_data['anatel_Titulo'] = ''
            logging.error(f"Error collecting title at index {index}: {e}")

        try:
            news_data['anatel_SubTitulo'] = format_html(news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').get_attribute('innerHTML'))
        except:
            news_data['anatel_SubTitulo'] = ''
            logging.error(f"Error collecting subtitle at index {index}")

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except:
            news_data['anatel_ImagemChamada'] = ''
            logging.error(f"Error collecting image at index {index}")

        try:
            news_data['anatel_Descricao'] = format_html(news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > span > span.data').get_attribute('innerHTML'))
        except:
            news_data['anatel_Descricao'] = ''
            logging.error(f"Error collecting description at index {index}")

        news_list.append(news_data)

    return news_list


def collect_news_details(news_url):
    driver.get(news_url)
    news_details = {}

    try:
        news_details['anatel_DataPublicacao'] = driver.find_element(
            By.CSS_SELECTOR, '#plone-document-byline > span.documentPublished').text.strip()
    except:
        news_details['anatel_DataPublicacao'] = ''
        logging.error(f"Error collecting publication date for URL: {news_url}")

    try:
        news_details['anatel_DataAtualizacao'] = driver.find_element(
            By.CSS_SELECTOR, '#plone-document-byline > span.documentModified').text.strip()
    except:
        news_details['anatel_DataAtualizacao'] = ''
        logging.error(f"Error collecting update date for URL: {news_url}")

    try:
        news_details['anatel_ImagemPrincipal'] = driver.find_element(
            By.CSS_SELECTOR, '#media > img').get_attribute('src')
    except:
        news_details['anatel_ImagemPrincipal'] = ''
        logging.error(f"Error collecting main image for URL: {news_url}")

    try:
        news_details['anatel_TextMateria'] = format_html(driver.find_element(
            By.CSS_SELECTOR, '#parent-fieldname-text > div').get_attribute('innerHTML'))
    except:
        news_details['anatel_TextMateria'] = ''
        logging.error(f"Error collecting article text for URL: {news_url}")

    try:
        news_details['anatel_Categoria'] = driver.find_element(
            By.CSS_SELECTOR, '#form-widgets-categoria').text.strip()
    except:
        news_details['anatel_Categoria'] = ''
        logging.error(f"Error collecting category for URL: {news_url}")

    return news_details


# Collect news from index
news_index = collect_news_index()

# Collect details for each news
for news in news_index:
    details = collect_news_details(news['anatel_URL'])
    news.update(details)

# Save news to MongoDB
for news in news_index:
    existing_news = news_collection.find_one(
        {'anatel_URL': news['anatel_URL']})
    if existing_news:
        if existing_news['anatel_DataAtualizacao'] != news['anatel_DataAtualizacao']:
            news_collection.update_one(
                {'anatel_URL': news['anatel_URL']}, {'$set': news})
    else:
        required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_SubTitulo', 'anatel_ImagemChamada', 'anatel_Descricao',
                           'anatel_DataPublicacao', 'anatel_ImagemPrincipal', 'anatel_TextMateria', 'anatel_Categoria']
        if all(news.get(field) for field in required_fields):
            news_collection.insert_one(news)
        else:
            news_collection_not_posted.insert_one(news)

# Close the Selenium driver
driver.quit()
