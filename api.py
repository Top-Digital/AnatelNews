import requests
from flask import Blueprint, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from anatel_news import collect_and_post_news

api_bp = Blueprint('api', __name__)

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client[os.getenv('DB_NAME')]
collection = db[os.getenv('NEWS_COLLECTION')]

WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')

def send_to_wordpress(news):
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Token': WEBHOOK_TOKEN
    }
    response = requests.post(WEBHOOK_URL, json=news, headers=headers)
    return response

@api_bp.route('/news/send', methods=['POST'])
def send_news():
    news = collection.find()
    for item in news:
        item['_id'] = str(item['_id'])  # Converter ObjectId para string
        response = send_to_wordpress(item)
        if response.status_code == 200:
            # Atualiza os campos de controle no MongoDB
            item['wordpressPostId'] = response.json().get('post_id')
            item['wordpress_DataPublicacao'] = datetime.now().isoformat()
            item['wordpress_AtualizacaoDetected'] = False
            item['wordpress_DataAtualizacao'] = item.get('anatel_DataAtualizacao')
            collection.update_one({'_id': item['_id']}, {"$set": item})
        else:
            return jsonify({'error': 'Failed to send news'}), 500
    return jsonify({'message': 'News sent successfully'}), 200

@api_bp.route('/news/collect', methods=['POST'])
def collect_news():
    collect_and_post_news()
    return jsonify({'message': 'News collected and posted successfully'}), 200
