import os
from dotenv import load_dotenv

# Defina a variável de ambiente `ENVIRONMENT` para o ambiente desejado, por exemplo:
# export ENVIRONMENT=local
# export ENVIRONMENT=prod
# export ENVIRONMENT=staging

environment = os.getenv('ENVAN', 'staging')  # Padrão para 'local' se não estiver definido

if environment == 'prod':
    dotenv_path = '.env.prod'
elif environment == 'staging':
    dotenv_path = '.env.staging'
else:
    dotenv_path = '.env.local'

load_dotenv(dotenv_path)