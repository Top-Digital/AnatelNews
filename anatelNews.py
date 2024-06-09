import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')
SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[NEWS_COLLECTION]

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
        except Exception as e:
            news_data['anatel_URL'] = ''
            print(f"Error collecting URL at index {index}: {e}")

        try:
            news_data['anatel_Titulo'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > h2 > a').get_attribute('innerHTML')
        except Exception as e:
            news_data['anatel_Titulo'] = ''
            print(f"Error collecting title at index {index}: {e}")
            # Print the HTML to debug why anatel_Titulo is empty
        print(
            f"News HTML at index {index}:\n{news_data['anatel_Titulo']}")

        try:
            news_data['anatel_SubTitulo'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.subtitulo-noticia').text
        except Exception as e:
            news_data['anatel_SubTitulo'] = ''
            print(f"Error collecting subtitle at index {index}: {e}")

        try:
            news_data['anatel_ImagemChamada'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > div.imagem.mobile > img').get_attribute('src')
        except Exception as e:
            news_data['anatel_ImagemChamada'] = ''
            print(f"Error collecting image at index {index}: {e}")

        try:
            news_data['anatel_Descricao'] = news.find_element(
                By.CSS_SELECTOR, 'div.conteudo > span > span.data').text
        except Exception as e:
            news_data['anatel_Descricao'] = ''
            print(f"Error collecting description at index {index}: {e}")

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

# Save news to MongoDB
for news in news_index:
    existing_news = collection.find_one({'anatel_URL': news['anatel_URL']})
    if existing_news:
        if existing_news['anatel_DataAtualizacao'] != news['anatel_DataAtualizacao']:
            collection.update_one(
                {'anatel_URL': news['anatel_URL']}, {'$set': news})
    else:
        collection.insert_one(news)

# Close the Selenium driver
driver.quit()
