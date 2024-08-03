import os
import requests
import json
from datetime import datetime
from mongoengine import Q
import mongoengine as me

from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conectar ao MongoDB usando variáveis de ambiente
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

me.connect(DB_NAME, host=MONGO_URI)

# Definir as coleções
from schemas.news_collection import NewsCollection

# Função para enviar dados para o WordPress
def send_to_wordpress(data):
    WORDPRESS_URL = os.getenv('WORDPRESS_URL', 'http://localhost:8000').rstrip('/')
    JWT_TOKEN = os.getenv('JWT_TOKEN')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JWT_TOKEN}'
    }

    create_post_url = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"
    response = requests.post(create_post_url, headers=headers, data=json.dumps(data))
    
    if response.status_code != 201:
        print(f"Erro ao criar post: {response.json()}")
    return response.json()

# Função para converter e enviar dados
def convert_and_send_fields():
    documents = NewsCollection.objects(
        Q(wordpressPostId__exists=False) | Q(wordpressPostId="")
    ).order_by('-anatel_DataPublicacao')
    for doc in documents:
        
        anatel_Descricao = doc.anatel_Descricao
        if type(doc.anatel_Descricao) != str:
            anatel_Descricao = doc.anatel_Descricao.isoformat() if doc.anatel_Descricao else ''
        
        anatel_DataPublicacao = doc.anatel_DataPublicacao
        if type(doc.anatel_DataPublicacao) != str:
            anatel_DataPublicacao = doc.anatel_DataPublicacao.isoformat() if doc.anatel_DataPublicacao else ''
        
        anatel_DataAtualizacao = doc.anatel_DataAtualizacao
        if type(doc.anatel_DataAtualizacao) != str:
            anatel_DataAtualizacao = doc.anatel_DataAtualizacao.isoformat() if doc.anatel_DataAtualizacao else ''
        
        anatel_wordpress_DataPublicacao = doc.wordpress_DataPublicacao
        if type(doc.wordpress_DataPublicacao) != str:
            anatel_wordpress_DataPublicacao = doc.wordpress_DataPublicacao.isoformat() if doc.wordpress_DataPublicacao else ''

        anatel_wordpress_DataAtualizacao = doc.wordpress_DataAtualizacao
        if type(doc.wordpress_DataAtualizacao) != str:
            anatel_wordpress_DataAtualizacao = doc.wordpress_DataAtualizacao.isoformat() if doc.wordpress_DataAtualizacao else ''
        
        anatel_mailchimp_DataEnvio = doc.mailchimp_DataEnvio
        if type(doc.mailchimp_DataEnvio) != str:
            anatel_mailchimp_DataEnvio = doc.mailchimp_DataEnvio.isoformat() if doc.mailchimp_DataEnvio else ''         

        data = {
            'title': doc.anatel_Titulo,
            'content': doc.anatel_TextMateria,
            'date': anatel_DataPublicacao,
            'meta': {
                'anatel_URL': doc.anatel_URL,
                'anatel_Titulo': doc.anatel_Titulo,
                'anatel_SubTitulo': doc.anatel_SubTitulo,
                'anatel_ImagemChamada': doc.anatel_ImagemChamada,
                'anatel_Descricao': anatel_Descricao,
                'anatel_DataPublicacao': anatel_DataPublicacao,
                'anatel_DataAtualizacao': anatel_DataAtualizacao,
                'anatel_ImagemPrincipal': doc.anatel_ImagemPrincipal,
                'anatel_TextMateria': doc.anatel_TextMateria,
                'anatel_Categoria': doc.anatel_Categoria,
                'wordpress_DataPublicacao': anatel_wordpress_DataPublicacao,
                'wordpress_DataAtualizacao': anatel_wordpress_DataAtualizacao,
                'mailchimp_DataEnvio': anatel_mailchimp_DataEnvio
            }
        }

        print(f"Enviando dados para o WordPress: {data}")

        response = send_to_wordpress(data)

        # Atualiza o post com o ID do post no WordPress para evitar duplicidade
        doc.wordpressPostId = str(response["id"])
        if doc.wordpress_DataAtualizacao:
            doc.wordpress_DataAtualizacao = datetime.now()
        else:
            doc.wordpress_DataPublicacao = datetime.now()

        doc.save()

if __name__ == '__main__':
    convert_and_send_fields()
