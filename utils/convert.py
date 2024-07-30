import mongoengine as me
from datetime import datetime

# Conectar ao MongoDB
me.connect('anatelnews', host='localhost', port=27017)  # ajuste o host e a porta conforme necessário

# Definir as coleções
from schemas.news_collection import NewsCollection

# Função para converter strings para os tipos corretos
def convert_fields():
    documents = NewsCollection.objects()
    for doc in documents:
        # Converting anatel_DataPublicacao
        if isinstance(doc.anatel_DataPublicacao, str):
            try:
                doc.anatel_DataPublicacao = datetime.strptime(doc.anatel_DataPublicacao, "Publicado em %d/%m/%Y %Hh%M")
            except ValueError:
                print(f"Formato desconhecido para anatel_DataPublicacao: {doc.anatel_DataPublicacao}")

        # Converting anatel_DataAtualizacao
        if doc.anatel_DataAtualizacao and isinstance(doc.anatel_DataAtualizacao, str):
            try:
                doc.anatel_DataAtualizacao = datetime.strptime(doc.anatel_DataAtualizacao, "Atualizado em %d/%m/%Y %Hh%M")
            except ValueError:
                print(f"Formato desconhecido para anatel_DataAtualizacao: {doc.anatel_DataAtualizacao}")
        else:
            doc.anatel_DataAtualizacao = None

        
        #anatel_Descricao Date format dd/mm/yyyy
        if isinstance(doc.anatel_Descricao, str):
            try:
                doc.anatel_Descricao = datetime.strptime(doc.anatel_Descricao, "%d/%m/%Y")
            except ValueError:
                print(f"Formato desconhecido para anatel_Descricao: {doc.anatel_Descricao}")    
        
        # Converting wordpress_DataPublicacao
        if doc.wordpress_DataPublicacao and isinstance(doc.wordpress_DataPublicacao, str):
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
            try:
                doc.mailchimp_DataEnvio = datetime.strptime(doc.mailchimp_DataEnvio, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    doc.mailchimp_DataEnvio = datetime.strptime(doc.mailchimp_DataEnvio, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    print(f"Formato desconhecido para mailchimp_DataEnvio: {doc.mailchimp_DataEnvio}")
        else:
            doc.mailchimp_DataEnvio = None


        if doc.mailchimpSent and isinstance(doc.mailchimpSent, str):
            doc.mailchimpSent = True if doc.mailchimpSent == "True" else False  
        else:
            doc.mailchimpSent = False


        if doc.mailchimp_DataEnvio and isinstance(doc.mailchimp_DataEnvio, str):
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
