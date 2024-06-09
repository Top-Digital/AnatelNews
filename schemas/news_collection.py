import mongoengine as me


class NewsCollection(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField(required=True)
    anatel_ImagemChamada = me.StringField(required=True)
    anatel_Descricao = me.StringField(required=True)
    anatel_DataPublicacao = me.StringField(required=True)
    anatel_DataAtualizacao = me.StringField(required=False)
    anatel_ImagemPrincipal = me.StringField(required=True)
    anatel_TextMateria = me.StringField(required=True)
    anatel_Categoria = me.StringField(required=True)

    meta = {
        'collection': 'news_collection'
    }
