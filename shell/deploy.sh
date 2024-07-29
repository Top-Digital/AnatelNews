#!/bin/bash

# Nome do container Docker do WordPress
CONTAINER_NAME="docker_wordpress_1" # Altere para o nome correto do seu container

# Diretório no container onde os plugins do WordPress estão localizados
CONTAINER_PLUGIN_DIR="/var/www/html/wp-content/plugins/anatelnews"

# Diretório local onde os novos arquivos do plugin estão localizados
LOCAL_PLUGIN_DIR="../wp-plugin" # Caminho relativo ao diretório shell

# Verifica se o container está em execução
if [ $(docker ps -q -f name=${CONTAINER_NAME}) ]; then
  echo "Container ${CONTAINER_NAME} está em execução. Continuando com a implantação..."
else
  echo "Container ${CONTAINER_NAME} não está em execução. Certifique-se de que o container Docker esteja em execução."
  exit 1
fi

# Apagar todos os arquivos e diretórios dentro de anatelnews no container
echo "Apagando arquivos antigos no container..."
docker exec -it ${CONTAINER_NAME} rm -rf ${CONTAINER_PLUGIN_DIR}/*

# Copiar todos os arquivos e diretórios do wp-plugin para o diretório anatelnews no container
echo "Copiando novos arquivos para o container..."
docker cp ${LOCAL_PLUGIN_DIR}/. ${CONTAINER_NAME}:${CONTAINER_PLUGIN_DIR}/

echo "Implantação concluída com sucesso!"
