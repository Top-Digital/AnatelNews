import os
import requests
import json
from datetime import datetime
import mongoengine as me
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conectar ao MongoDB usando variáveis de ambiente
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')

me.connect(DB_NAME, host=MONGO_URI)  # Ajuste conforme necessário

# Definir as coleções
class NewsCollection(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField(required=True)
    anatel_ImagemChamada = me.StringField(required=True)
    anatel_Descricao = me.StringField(required=True)
    anatel_DataPublicacao = me.DateTimeField(required=True)
    anatel_DataAtualizacao = me.DateTimeField(required=False, default=None)
    anatel_ImagemPrincipal = me.StringField(required=True)
    anatel_TextMateria = me.StringField(required=True)
    anatel_Categoria = me.StringField(required=True)
    wordpressPostId = me.StringField(required=False, default=None)
    wordpress_DataPublicacao = me.DateTimeField(required=False, default=None)
    wordpress_DataAtualizacao = me.DateTimeField(required=False, default=None)
    wordpress_AtualizacaoDetected = me.BooleanField(required=False, default=None)
    mailchimpSent = me.BooleanField(required=False, default=None)
    mailchimp_DataEnvio = me.DateTimeField(required=False, default=None)
    
    meta = {
        'collection': NEWS_COLLECTION
    }

def serialize_dates(data):
    """Converte todos os campos datetime para strings ISO 8601"""
    for key, value in data.items():
        if isinstance(value, datetime):
            data[key] = value.isoformat()
        elif isinstance(value, dict):
            data[key] = serialize_dates(value)
    return data

# Função para enviar dados para o WordPress
def send_to_wordpress(data):
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    WEBHOOK_TOKEN = os.getenv('WEBHOOK_TOKEN')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEBHOOK_TOKEN}'
    }

    # Converter datas para strings ISO
    data = serialize_dates(data)
    
    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data))
    return response.json()

# Função para converter e enviar dados
def convert_and_send_fields():
    documents = NewsCollection.objects()
    for doc in documents:
        data = {
            'title': doc.anatel_Titulo,
            'content': doc.anatel_TextMateria,
            'meta': {
                'anatel_URL': doc.anatel_URL,
                'anatel_Titulo': doc.anatel_Titulo,
                'anatel_SubTitulo': doc.anatel_SubTitulo,
                'anatel_ImagemChamada': doc.anatel_ImagemChamada,
                'anatel_Descricao': doc.anatel_Descricao,
                'anatel_DataPublicacao': doc.anatel_DataPublicacao,
                'anatel_DataAtualizacao': doc.anatel_DataAtualizacao,
                'anatel_ImagemPrincipal': doc.anatel_ImagemPrincipal,
                'anatel_TextMateria': doc.anatel_TextMateria,
                'anatel_Categoria': doc.anatel_Categoria,
                'wordpress_DataPublicacao': doc.wordpress_DataPublicacao,
                'wordpress_DataAtualizacao': doc.wordpress_DataAtualizacao,
                'mailchimp_DataEnvio': doc.mailchimp_DataEnvio
            }
        }
        response = send_to_wordpress(data)
        print(response)

if __name__ == '__main__':
    convert_and_send_fields()
