import requests
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import sendgrid
from sendgrid.helpers.mail import Mail
from schemas.news_collection import NewsCollection
from schemas.news_collection_not_posted import NewsCollectionNotPosted
from config.config import MONGO_URI, DB_NAME, NEWS_COLLECTION, NEWS_COLLECTION_NOT_POSTED, WEBHOOK_URL, WEBHOOK_TOKEN, SENDGRID_API_KEY, LOG_FILE

app = Flask(__name__)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[NEWS_COLLECTION]
not_posted_collection = db[NEWS_COLLECTION_NOT_POSTED]

sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

def send_to_wordpress(news):
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Token': WEBHOOK_TOKEN
    }
    attribution = '''
    <div class="texto-copyright">
        Todo o conteúdo deste site está publicado sob a licença <a rel="license" href="https://creativecommons.org/licenses/by-nd/3.0/deed.pt_BR">Creative Commons Atribuição-SemDerivações 3.0 Não Adaptada</a>. 
        Fonte: <a href="{url}" target="_blank">Anatel</a>.
    </div>
    '''.format(url=news['anatel_URL'])
    news['anatel_TextMateria'] += attribution
    response = requests.post(WEBHOOK_URL, json=news, headers=headers)
    return response

def send_email(to, subject, content):
    message = Mail(
        from_email='seuemail@seudominio.com',
        to_emails=to,
        subject=subject,
        html_content=content)
    try:
        response = sg.send(message)
        return response.status_code == 202
    except Exception as e:
        print(e.message)
        return False

@app.route('/news/send', methods=['POST'])
def send_news():
    # Verifica notícias na coleção principal
    news = collection.find()
    required_fields = ['anatel_URL', 'anatel_Titulo', 'anatel_DataPublicacao', 'anatel_TextMateria']
    
    for item in news:
        if all(item.get(field) for field in required_fields):
            if not item.get('email_sent', False):  # Verifica se o email já foi enviado
                item['_id'] = str(item['_id'])  # Converter ObjectId para string
                if send_email("destinatario@exemplo.com", item['anatel_Titulo'], item['anatel_TextMateria']):
                    item['email_sent'] = True
                    item['email_sent_at'] = datetime.now()
                    collection.update_one({'_id': item['_id']}, {"$set": item})
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

    # Verifica notícias na coleção de não publicadas
    not_posted_news = not_posted_collection.find()
    
    for item in not_posted_news:
        if all(item.get(field) for field in required_fields):
            item['_id'] = str(item['_id'])  # Converter ObjectId para string
            if send_email("destinatario@exemplo.com", item['anatel_Titulo'], item['anatel_TextMateria']):
                item['email_sent'] = True
                item['email_sent_at'] = datetime.now()
                collection.insert_one(item)
                not_posted_collection.delete_one({'_id': item['_id']})
                # Atualiza os campos de controle no MongoDB
                item['wordpressPostId'] = response.json().get('post_id')
                item['wordpress_DataPublicacao'] = datetime.now().isoformat()
                item['wordpress_AtualizacaoDetected'] = False
                item['wordpress_DataAtualizacao'] = item.get('anatel_DataAtualizacao')
                collection.update_one({'_id': item['_id']}, {"$set": item})
            else:
                return jsonify({'error': 'Failed to send news'}), 500

    return jsonify({'message': 'News sent successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
