import os
import mongoengine as me

# Load environment variables
NEWS_COLLECTION_NOT_POSTED = os.getenv('NEWS_COLLECTION_NOT_POSTED')


class NewsCollectionNotPosted(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=False)
    anatel_SubTitulo = me.StringField(required=False)
    anatel_ImagemChamada = me.StringField(required=False)
    anatel_Descricao = me.StringField(required=False)
    anatel_DataPublicacao = me.StringField(required=False)
    anatel_DataAtualizacao = me.StringField(required=False)
    anatel_ImagemPrincipal = me.StringField(required=False)
    anatel_TextMateria = me.StringField(required=False)
    anatel_Categoria = me.StringField(required=False)

    meta = {
        'collection': NEWS_COLLECTION_NOT_POSTED
    }
