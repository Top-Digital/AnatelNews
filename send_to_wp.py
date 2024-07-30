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

def get_category_id(category_name):
    """Verifica se a categoria existe e retorna seu ID"""
    WORDPRESS_URL = os.getenv('WORDPRESS_URL').rstrip('/')
    JWT_TOKEN = os.getenv('JWT_TOKEN')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }

    # Verificar se a categoria já existe
    categories_url = f"{WORDPRESS_URL}/wp-json/wp/v2/categories?search={category_name}"
    response = requests.get(categories_url, headers=headers)
    
    try:
        categories = response.json()
        print(f"Categorias retornadas: {categories}")  # Log para depuração
    except ValueError:
        print(f"Erro ao decodificar JSON: {response.text}")
        categories = []

    if isinstance(categories, list) and any(cat['name'] == category_name for cat in categories):
        return next(cat['id'] for cat in categories if cat['name'] == category_name)
    else:
        print("Erro: Categoria 'Notícias Anatel – NewsLetter' não encontrada.")
        return None

# Função para enviar dados para o WordPress
def send_to_wordpress(data):
    WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'http://localhost:8000').rstrip('/')
    JWT_TOKEN = os.getenv('JWT_TOKEN')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }

    # Converter datas para strings ISO
    data = serialize_dates(data)

    # Garantir que a categoria "Notícias Anatel – NewsLetter" existe
    category_id = 2
    if category_id:
        data['categories'] = [category_id]
    else:
        print("Erro: Não foi possível encontrar a categoria 'Notícias Anatel – NewsLetter'.")
        return {"error": "Não foi possível encontrar a categoria 'Notícias Anatel – NewsLetter'."}
    
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
        response = send_to_wordpress(data)
        print(response)

if __name__ == '__main__':
    convert_and_send_fields()
