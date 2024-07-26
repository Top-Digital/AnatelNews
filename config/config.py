import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')
NEWS_COLLECTION_NOT_POSTED = os.getenv('NEWS_COLLECTION_NOT_POSTED')
SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'
LOG_FILE = os.getenv('LOG_FILE')
NEWS_URL = os.getenv('NEWS_URL')
