import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import mongoengine as me

# Import the schemas
from schemas.news_collection import NewsCollection
from schemas.news_collection_not_posted import NewsCollectionNotPosted

# Load environment variables
load_dotenv()

SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'

# MongoDB connection
me.connect(db='anatelnews', host='localhost', port=27017)

# Selenium setup
options = Options()
if not SHOW_BROWSER:
    options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(
    '/usr/local/bin/chromedriver'), options=options)

# Drop collections
NewsCollection.drop_collection()
NewsCollectionNotPosted.drop_collection()


# Function to collect news index
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

        try:
            news_data['anatel_Titulo'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('innerHTML')
        except Exception as e:
            news_data['anatel_Titulo'] = ''

        try:
            news_data['anatel_SubTitulo'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').get_attribute('innerHTML')
        except:
            news_data['anatel_SubTitulo'] = ''

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except:
            news_data['anatel_ImagemChamada'] = ''

        try:
            news_data['anatel_Descricao'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > span.descricao').get_attribute('innerHTML')
        except:
            news_data['anatel_Descricao'] = ''

        news_list.append(news_data)

    return news_list


# Function to collect news details
def collect_news_details(news_url):
    driver.get(news_url)
    news_details = {}

    try:
        news_details['anatel_DataPublicacao'] = driver.find_element(
            By.CSS_SELECTOR, '#plone-document-byline > span.documentPublished').text
    except:
        news_details['anatel_DataPublicacao'] = ''

    try:
        news_details['anatel_DataAtualizacao'] = driver.find_element(
            By.CSS_SELECTOR, '#plone-document-byline > span.documentModified').text
    except:
        news_details['anatel_DataAtualizacao'] = ''

    try:
        news_details['anatel_ImagemPrincipal'] = driver.find_element(
            By.CSS_SELECTOR, '#media > img').get_attribute('src')
    except:
        news_details['anatel_ImagemPrincipal'] = ''

    try:
        news_details['anatel_TextMateria'] = driver.find_element(
            By.CSS_SELECTOR, '#parent-fieldname-text > div').get_attribute('innerHTML')
    except:
        news_details['anatel_TextMateria'] = ''

    try:
        news_details['anatel_Categoria'] = driver.find_element(
            By.CSS_SELECTOR, '#form-widgets-categoria').get_attribute('innerHTML')
    except:
        news_details['anatel_Categoria'] = ''

    return news_details


# Function to validate news data
def is_valid_news(news_data):
    required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_SubTitulo', 'anatel_ImagemChamada', 'anatel_Descricao',
                       'anatel_DataPublicacao', 'anatel_ImagemPrincipal', 'anatel_TextMateria', 'anatel_Categoria']
    for field in required_fields:
        if not news_data.get(field):
            return False
    return True


# Collect news from index
news_index = collect_news_index()

# Collect details for each news
for news in news_index:
    details = collect_news_details(news['anatel_URL'])
    news.update(details)

    if is_valid_news(news):
        existing_news = NewsCollection.objects(
            anatel_URL=news['anatel_URL']).first()
        if existing_news:
            if existing_news.anatel_DataAtualizacao != news['anatel_DataAtualizacao']:
                existing_news.update(**news)
        else:
            news_doc = NewsCollection(**news)
            news_doc.save()
    else:
        existing_news = NewsCollectionNotPosted.objects(
            anatel_URL=news['anatel_URL']).first()
        if existing_news:
            existing_news.update(**news)
        else:
            news_doc = NewsCollectionNotPosted(**news)
            news_doc.save()

# Close the Selenium driver
driver.quit()
