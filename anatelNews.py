import os
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import mongoengine as me
from schemas.news_collection import NewsCollection
from schemas.news_collection_not_posted import NewsCollectionNotPosted
from config.config import MONGO_URI, DB_NAME, SHOW_BROWSER, LOG_FILE, NEWS_URL

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress overly detailed logging from external libraries
logging.getLogger('selenium').setLevel(logging.WARNING)

# MongoDB connection with mongoengine
me.connect(db=DB_NAME, host=MONGO_URI)

# Selenium setup
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

def collect_news_index(page_number):
    url = f"{NEWS_URL}{page_number * 30}"
    print(f"Collecting news from URL: {url}")
    driver.get(url)
    news_list = []
    news_elements = driver.find_elements(By.CSS_SELECTOR, '#ultimas-noticias > ul.noticias.listagem-noticias-com-foto > li')

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

# Collect news from all pages
news_index = []
for page in range(0, 34):  # 34 pages will give us 1020 news
    news_index.extend(collect_news_index(page))

# Collect details for each news
for news in news_index:
    if news['anatel_URL']:
        details = collect_news_details(news['anatel_URL'])
        news.update(details)

# Save news to MongoDB
for news in news_index:
    existing_news = NewsCollection.objects(anatel_URL=news['anatel_URL']).first()
    if existing_news:
        if existing_news.anatel_DataAtualizacao != news['anatel_DataAtualizacao']:
            existing_news.update(**news)
    else:
        required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_SubTitulo', 'anatel_ImagemChamada', 'anatel_Descricao',
                           'anatel_DataPublicacao', 'anatel_ImagemPrincipal', 'anatel_TextMateria', 'anatel_Categoria']
        if all(news.get(field) for field in required_fields):
            NewsCollection(**news).save()
        else:
            NewsCollectionNotPosted(**news).save()

# Close the Selenium driver
driver.quit()
