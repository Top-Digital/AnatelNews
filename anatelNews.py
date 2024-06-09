import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import mongoengine as me

# Load environment variables
load_dotenv()

SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'

# MongoDB connection
me.connect(db='anatel_news', host='localhost', port=27017)

# Definição do Modelo de Notícia


class News(me.Document):
    anatel_URL = me.StringField(required=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField()
    anatel_ImagemChamada = me.StringField()
    anatel_Descricao = me.StringField()
    anatel_DataPublicacao = me.StringField()
    anatel_DataAtualizacao = me.StringField()
    anatel_ImagemPrincipal = me.StringField()
    anatel_TextMateria = me.StringField()
    anatel_Categoria = me.StringField()

    meta = {
        'collection': 'news_collection'
    }


# Selenium setup
options = Options()
if not SHOW_BROWSER:
    options.add_argument('--headless')

driver = webdriver.Chrome(service=Service(
    '/usr/local/bin/chromedriver'), options=options)

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
            print(f"Error collecting title at index {index}: {e}")

        try:
            news_data['anatel_SubTitulo'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').text
        except:
            news_data['anatel_SubTitulo'] = ''

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except:
            news_data['anatel_ImagemChamada'] = ''

        try:
            news_data['anatel_Descricao'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > span > span.data').text
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
            By.CSS_SELECTOR, '#parent-fieldname-text > div').text
    except:
        news_details['anatel_TextMateria'] = ''

    try:
        news_details['anatel_Categoria'] = driver.find_element(
            By.CSS_SELECTOR, '#formfield-form-widgets-categoria').text
    except:
        news_details['anatel_Categoria'] = ''

    return news_details


# Collect news from index
news_index = collect_news_index()

# Collect details for each news
for news in news_index:
    details = collect_news_details(news['anatel_URL'])
    news.update(details)
    # Save news to MongoDB using mongoengine
    news_doc = News(**news)
    news_doc.save()

# Close the Selenium driver
driver.quit()
