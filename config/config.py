import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
SHOW_BROWSER = os.getenv('SHOW_BROWSER') == 'true'
LOG_FILE = os.getenv('LOG_FILE')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
