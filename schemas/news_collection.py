import mongoengine as me
from config.config import NEWS_COLLECTION

class NewsCollection(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField(required=True)
    anatel_ImagemChamada = me.StringField(required=True)
    anatel_Descricao = me.DateTimeField(required=True)
    anatel_DataPublicacao = me.DateTimeField(required=True)
    anatel_DataAtualizacao = me.DateTimeField(required=False, default=None)
    anatel_ImagemPrincipal = me.StringField(required=True)
    anatel_TextMateria = me.StringField(required=True)
    anatel_Categoria = me.StringField(required=True)
    anatel_PostIsRemoved = me.BooleanField(required=True, default=False)
    anatel_ErrorToFix = me.BooleanField(required=True, default=False)
    anatel_ErrorDescription = me.StringField(required=False, default=None)
    anatel_ErrorDate = me.DateTimeField(required=False, default=None)
    anatel_lastOnechecked = me.DateTimeField(required=False, default=None)
    wordpressPostId = me.StringField(required=False, default=None)
    wordpress_DataPublicacao = me.DateTimeField(required=False, default=None)
    wordpress_AtualizacaoDetected = me.BooleanField(required=False, default=None)
    wordpress_DataAtualizacao = me.DateTimeField(required=False, default=None)
    mailchimpSent = me.BooleanField(required=False, default=None)
    mailchimp_DataEnvio = me.DateTimeField(required=False, default=None)

    meta = {
        'collection': NEWS_COLLECTION
    }
