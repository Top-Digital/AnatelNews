import os
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost
from wordpress_xmlrpc.methods.taxonomies import GetTerms
from datetime import datetime
from mongoengine import Q
import mongoengine as me
from config import env

# Conectar ao MongoDB usando variáveis de ambiente
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')

me.connect(DB_NAME, host=MONGO_URI)

# Definir as coleções
from schemas.news_collection import NewsCollection

# Conectar ao WordPress
WORDPRESS_URL = os.getenv('WORDPRESS_URL')
WORDPRESS_USER = os.getenv('WORDPRESS_USER')
WORDPRESS_PASSWORD = os.getenv('WORDPRESS_PASSWORD')

client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)

# Obter a ID da categoria "Anatel News"
def get_category_id(category_name):
    categories = client.call(GetTerms('category'))
    for category in categories:
        if category.name == category_name:
            return category.id
    return None

# ID da categoria "Anatel News"
CATEGORY_ID = get_category_id('Anatel News')

# Função para enviar dados para o WordPress
def send_to_wordpress(post):
    wp_post = WordPressPost()
    wp_post.title = post['title']
    wp_post.content = post['content']
    wp_post.post_status = 'publish'
    wp_post.date = post['date']
    wp_post.terms_names = {'category': ['Anatel News']}  # Associa a categoria pelo nome
    wp_post.custom_fields = [
        {'key': 'anatel_URL', 'value': post['meta']['anatel_URL']},
        {'key': 'anatel_Titulo', 'value': post['meta']['anatel_Titulo']},
        {'key': 'anatel_SubTitulo', 'value': post['meta']['anatel_SubTitulo']},
        {'key': 'anatel_ImagemChamada', 'value': post['meta']['anatel_ImagemChamada']},
        {'key': 'anatel_Descricao', 'value': post['meta']['anatel_Descricao']},
        {'key': 'anatel_DataPublicacao', 'value': post['meta']['anatel_DataPublicacao']},
        {'key': 'anatel_DataAtualizacao', 'value': post['meta']['anatel_DataAtualizacao']},
        {'key': 'anatel_ImagemPrincipal', 'value': post['meta']['anatel_ImagemPrincipal']},
        {'key': 'anatel_TextMateria', 'value': post['meta']['anatel_TextMateria']},
        {'key': 'anatel_Categoria', 'value': post['meta']['anatel_Categoria']},
        {'key': 'wordpress_DataPublicacao', 'value': post['meta']['wordpress_DataPublicacao']},
        {'key': 'wordpress_DataAtualizacao', 'value': post['meta']['wordpress_DataAtualizacao']},
        {'key': 'mailchimp_DataEnvio', 'value': post['meta']['mailchimp_DataEnvio']}
    ]
    return client.call(NewPost(wp_post))

# Função para converter e enviar dados
def convert_and_send_fields():
    documents = NewsCollection.objects(
        Q(wordpressPostId__exists=False) | Q(wordpressPostId="")
    ).order_by('-anatel_DataPublicacao').limit(10)
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

        # Verificar se a resposta contém o ID do post
        if response and hasattr(response, 'id'):
            # Atualiza o post com o ID do post no WordPress para evitar duplicidade
            doc.wordpressPostId = str(response.id)
            if doc.wordpress_DataAtualizacao:
                doc.wordpress_DataAtualizacao = datetime.now()
            else:
                doc.wordpress_DataPublicacao = datetime.now()

            doc.save()
        else:
            print("Erro ao enviar dados para o WordPress. Nenhuma atualização feita no MongoDB.")

if __name__ == '__main__':
    convert_and_send_fields()
