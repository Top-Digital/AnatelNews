#!/bin/bash

# Diretório local onde os arquivos do plugin estão localizados
LOCAL_PLUGIN_DIR="/home/adriano/dev/anatelnews/wp-plugin"
LOCAL_WP_PLUGIN_DIR="/home/adriano/dev/anatelnews/docker/wp_data/wp-content/plugins"
DESTINATION_ZIP_DIR="/home/adriano/Downloads"

# Nome do arquivo .zip do plugin
PLUGIN_ZIP="anatelnews.zip"

# Navegar para o diretório onde os arquivos do plugin estão localizados
cd "$LOCAL_PLUGIN_DIR" || {
  echo "Erro ao acessar o diretório $LOCAL_PLUGIN_DIR"
  exit 1
}

# Navegar para o diretório onde os plugins do WordPress estão localizados
cd "$LOCAL_WP_PLUGIN_DIR" || {
  echo "Erro ao acessar o diretório $LOCAL_WP_PLUGIN_DIR"
  exit 1
}

# Remover arquivos antigos do plugin
echo "Removendo arquivos antigos do plugin..."
rm -rf anatelnews

# Recriar o diretório do plugin
echo "Recriando o diretório do plugin..."
mkdir anatelnews

# Copiar os arquivos do diretório local para o diretório do plugin no WordPress
echo "Copiando arquivos do plugin para o diretório do WordPress..."
cp -r "$LOCAL_PLUGIN_DIR"/* anatelnews

# Dar permissões corretas para o diretório do plugin
echo "Ajustando permissões do diretório do plugin..."
chown -R www-data:www-data anatelnews
chmod -R 755 anatelnews

# Criar o arquivo .zip do plugin
echo "Criando arquivo .zip do plugin..."
zip -r "$PLUGIN_ZIP" anatelnews*

# Mover o arquivo .zip para o diretório de downloads
echo "Movendo o arquivo .zip para $DESTINATION_ZIP_DIR..."
mv "$PLUGIN_ZIP" "$DESTINATION_ZIP_DIR"

echo "Implantação concluída com sucesso!"
