from flask import Flask, jsonify
from mongoengine import Q
from datetime import datetime
import mongoengine as me
from config.config import MONGO_URI, DB_NAME, WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD
from schemas.news_collection import NewsCollection
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, EditPost, DeletePost

app = Flask(__name__)

# Conectar ao MongoDB
me.connect(DB_NAME, host=MONGO_URI)

# Conectar ao WordPress
client = Client(WORDPRESS_URL, WORDPRESS_USER, WORDPRESS_PASSWORD)

@app.route('/getnewposts', methods=['GET', 'POST'])
def get_new_posts():
    try:
        documents = NewsCollection.objects(
            (Q(wordpressPostId__exists=False) | Q(wordpressPostId="")) & Q(anatel_ErrorToFix=False)
        ).order_by('-anatel_DataPublicacao')

        posts = []
        for doc in documents:
            if not doc.anatel_Titulo or not doc.anatel_TextMateria or not doc.anatel_DataPublicacao:
                doc.update(
                    set__anatel_ErrorToFix=True,
                    set__anatel_ErrorDescription='Missing required fields',
                    set__anatel_ErrorDate=datetime.now()
                )
                continue

            post_data = {
                'title': doc.anatel_Titulo,
                'content': doc.anatel_TextMateria,
                'date': doc.anatel_DataPublicacao,
                'meta': {
                    'anatel_URL': doc.anatel_URL,
                    'anatel_SubTitulo': doc.anatel_SubTitulo,
                    'anatel_ImagemChamada': doc.anatel_ImagemChamada,
                    'anatel_Descricao': doc.anatel_Descricao,
                    'anatel_DataAtualizacao': doc.anatel_DataAtualizacao,
                    'anatel_ImagemPrincipal': doc.anatel_ImagemPrincipal,
                    'anatel_Categoria': doc.anatel_Categoria
                }
            }

            try:
                if doc.anatel_PostIsRemoved:
                    if doc.wordpressPostId:
                        client.call(DeletePost(doc.wordpressPostId))
                        doc.update(
                            set__wordpress_DataAtualizacao=datetime.now()
                        )
                    post_data['action'] = 'delete'
                elif doc.anatel_DataAtualizacao and doc.anatel_DataAtualizacao > doc.anatel_DataPublicacao:
                    if doc.wordpressPostId:
                        wp_post = WordPressPost()
                        wp_post.id = doc.wordpressPostId
                        wp_post.title = doc.anatel_Titulo
                        wp_post.content = doc.anatel_TextMateria
                        wp_post.date = doc.anatel_DataPublicacao
                        wp_post.custom_fields = [
                            {'key': key, 'value': value} for key, value in post_data['meta'].items()
                        ]
                        client.call(EditPost(wp_post.id, wp_post))
                        doc.update(
                            set__wordpress_DataAtualizacao=datetime.now()
                        )
                    post_data['action'] = 'update'
                else:
                    wp_post = WordPressPost()
                    wp_post.title = doc.anatel_Titulo
                    wp_post.content = doc.anatel_TextMateria
                    wp_post.date = doc.anatel_DataPublicacao
                    wp_post.custom_fields = [
                        {'key': key, 'value': value} for key, value in post_data['meta'].items()
                    ]
                    response = client.call(NewPost(wp_post))
                    doc.update(
                        set__wordpressPostId=str(response),
                        set__wordpress_DataPublicacao=datetime.now()
                    )
                    post_data['action'] = 'create'

                posts.append(post_data)
            except Exception as e:
                doc.update(
                    set__anatel_ErrorToFix=True,
                    set__anatel_ErrorDescription=str(e),
                    set__anatel_ErrorDate=datetime.now()
                )
                return jsonify({'error': str(e)}), 500

        return jsonify(posts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
