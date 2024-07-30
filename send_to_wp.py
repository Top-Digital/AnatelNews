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
WORDPRESS_URL = os.getenv('WORDPRESS_URL')

JWT_TOKEN = os.getenv('JWT_TOKEN')

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {JWT_TOKEN}'
}

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
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }

    # Converter datas para strings ISO
    data = serialize_dates(data)

    # Usar a categoria com ID 2
    data['categories'] = [2]
    data['status'] = 'publish'  # Garantir que os posts sejam publicados
    
    create_post_url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
    response = requests.post(create_post_url, headers=headers, data=json.dumps(data))
    
    if response.status_code != 201:
        print(f"Erro ao criar post: {response.json()}")
    return response.json()

# Função para converter e enviar dados
def convert_and_send_fields():
    cutoff_date = datetime.strptime('2024-06-28T18:47:00.000+00:00', '%Y-%m-%dT%H:%M:%S.%f%z')
    documents = NewsCollection.objects().order_by('-anatel_DataPublicacao')
    for doc in documents:
        if doc.anatel_DataAtualizacao and doc.anatel_DataAtualizacao >= cutoff_date:
            doc.mailchimpSent = True
            doc.mailchimp_DataEnvio = datetime.now()
            doc.save()
        
        data = {
            'title': doc.anatel_Titulo,
            'content': doc.anatel_TextMateria,
            'date': doc.anatel_DataPublicacao.isoformat() if doc.anatel_DataPublicacao else '',  # Usar anatel_DataPublicacao como data de publicação
            'meta': {
                'anatel_URL': doc.anatel_URL,
                'anatel_Titulo': doc.anatel_Titulo,
                'anatel_SubTitulo': doc.anatel_SubTitulo,
                'anatel_ImagemChamada': doc.anatel_ImagemChamada,
                'anatel_Descricao': doc.anatel_Descricao,
                'anatel_DataPublicacao': doc.anatel_DataPublicacao.isoformat() if doc.anatel_DataPublicacao else '',
                'anatel_DataAtualizacao': doc.anatel_DataAtualizacao.isoformat() if doc.anatel_DataAtualizacao else '',
                'anatel_ImagemPrincipal': doc.anatel_ImagemPrincipal,
                'anatel_TextMateria': doc.anatel_TextMateria,
                'anatel_Categoria': doc.anatel_Categoria,
                'wordpress_DataPublicacao': doc.wordpress_DataPublicacao.isoformat() if doc.wordpress_DataPublicacao else '',
                'wordpress_DataAtualizacao': doc.wordpress_DataAtualizacao.isoformat() if doc.wordpress_DataAtualizacao else '',
                'mailchimp_DataEnvio': doc.mailchimp_DataEnvio.isoformat() if doc.mailchimp_DataEnvio else ''
            }
        }
        
        # Verificar se o post já existe no WordPress
        if doc.wordpressPostId:
            update_post_url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts/{doc.wordpressPostId}"
            response = requests.post(update_post_url, headers=headers, data=json.dumps(data))
        else:
            response = send_to_wordpress(data)
            if 'id' in response:
                doc.wordpressPostId = response['id']
                doc.save()

        print(response)

if __name__ == '__main__':
    convert_and_send_fields()
