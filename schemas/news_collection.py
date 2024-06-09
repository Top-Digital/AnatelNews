import os
import mongoengine as me
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
NEWS_COLLECTION = os.getenv('NEWS_COLLECTION')


class NewsCollection(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField(required=True)
    anatel_ImagemChamada = me.StringField(required=True)
    anatel_Descricao = me.StringField(required=True)
    anatel_DataPublicacao = me.StringField(required=True)
    anatel_DataAtualizacao = me.StringField()
    anatel_ImagemPrincipal = me.StringField(required=True)
    anatel_TextMateria = me.StringField(required=True)
    anatel_Categoria = me.StringField(required=True)

    meta = {
        'collection': NEWS_COLLECTION
    }
