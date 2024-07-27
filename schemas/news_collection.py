import mongoengine as me
from config.config import NEWS_COLLECTION

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
    wordpressPostId = me.StringField(required=False)
    wordpress_DataPublicacao = me.StringField(required=False)
    wordpress_AtualizacaoDetected = me.BooleanField(required=False)
    wordpress_DataAtualizacao = me.StringField(required=False)

    meta = {
        'collection': NEWS_COLLECTION
    }
