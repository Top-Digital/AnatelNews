import mongoengine as me
from datetime import datetime

# Conectar ao MongoDB
me.connect('anatelnews', host='localhost', port=27017)  # ajuste o host e a porta conforme necessário

# Definir as coleções
class NewsCollection(me.Document):
    anatel_URL = me.StringField(required=True, unique=True, index=True)
    anatel_Titulo = me.StringField(required=True)
    anatel_SubTitulo = me.StringField(required=True)
    anatel_ImagemChamada = me.StringField(required=True)
    anatel_Descricao = me.StringField(required=True)
    anatel_DataPublicacao = me.DateTimeField(required=True)
    anatel_DataAtualizacao = me.DateTimeField()
    anatel_ImagemPrincipal = me.StringField(required=True)
    anatel_TextMateria = me.StringField(required=True)
    anatel_Categoria = me.StringField(required=True)
    wordpressPostId = me.StringField()
    wordpress_DataPublicacao = me.DateTimeField()
    wordpress_DataAtualizacao = me.DateTimeField()
    wordpress_AtualizacaoDetected = me.BooleanField()
    mailchimpSent = me.BooleanField()
    mailchimp_DataEnvio = me.DateTimeField()

    meta = {
        'collection': 'news'
    }

# Função para converter strings para os tipos corretos
def convert_fields():
    documents = NewsCollection.objects()
    for doc in documents:
        print(doc.anatel_DataAtualizacao)
        # Converting anatel_DataPublicacao
        if isinstance(doc.anatel_DataPublicacao, str):
            doc.anatel_DataPublicacao = datetime.strptime(doc.anatel_DataPublicacao, "Publicado em %d/%m/%Y %Hh%M")
        
        # Converting anatel_DataAtualizacao

            if doc.anatel_DataAtualizacao and isinstance(doc.anatel_DataAtualizacao, str):
                try:
                    doc.anatel_DataAtualizacao = datetime.strptime(doc.anatel_DataAtualizacao, "Atualizado em %d/%m/%Y %Hh%M")
                except ValueError:
                    print(f"Formato desconhecido para anatel_DataAtualizacao: {doc.anatel_DataAtualizacao}")
            else:                
                doc.anatel_DataAtualizacao = None
        
        # Converting wordpress_DataPublicacao
        if doc.wordpress_DataPublicacao and isinstance(doc.wordpress_DataPublicacao, str):
            if doc.wordpress_DataPublicacao.strip() != "":
                try:
                    doc.wordpress_DataPublicacao = datetime.strptime(doc.wordpress_DataPublicacao, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        doc.wordpress_DataPublicacao = datetime.strptime(doc.wordpress_DataPublicacao, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        print(f"Formato desconhecido para wordpress_DataPublicacao: {doc.wordpress_DataPublicacao}")
            else:
                doc.wordpress_DataPublicacao = None
        
        # Converting wordpress_DataAtualizacao
        if doc.wordpress_DataAtualizacao and isinstance(doc.wordpress_DataAtualizacao, str):
            if doc.wordpress_DataAtualizacao.strip() != "":
                try:
                    doc.wordpress_DataAtualizacao = datetime.strptime(doc.wordpress_DataAtualizacao, "Atualizado em %d/%m/%Y %Hh%M")
                except ValueError:
                    try:
                        doc.wordpress_DataAtualizacao = datetime.strptime(doc.wordpress_DataAtualizacao, "%Y-%m-%dT%H:%M:%S.%fZ")
                    except ValueError:
                        try:
                            doc.wordpress_DataAtualizacao = datetime.strptime(doc.wordpress_DataAtualizacao, "%Y-%m-%dT%H:%M:%S.%f")
                        except ValueError:
                            print(f"Formato desconhecido para wordpress_DataAtualizacao: {doc.wordpress_DataAtualizacao}")
            else:
                doc.wordpress_DataAtualizacao = None
        
        # Converting mailchimp_DataEnvio
        if doc.mailchimp_DataEnvio and isinstance(doc.mailchimp_DataEnvio, str):
            if doc.mailchimp_DataEnvio.strip() != "":
                try:
                    doc.mailchimp_DataEnvio = datetime.strptime(doc.mailchimp_DataEnvio, "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    try:
                        doc.mailchimp_DataEnvio = datetime.strptime(doc.mailchimp_DataEnvio, "%Y-%m-%dT%H:%M:%S.%f")
                    except ValueError:
                        print(f"Formato desconhecido para mailchimp_DataEnvio: {doc.mailchimp_DataEnvio}")
            else:
                doc.mailchimp_DataEnvio = None

        # Atualizar o documento no banco de dados
        doc.save()

if __name__ == '__main__':
    convert_fields()
