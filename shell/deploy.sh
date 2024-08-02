#!/bin/bash

# Diretório local onde os arquivos do plugin estão localizados
LOCAL_PLUGIN_DIR="/home/adriano/dev/AnatelNews/wp-plugin"

# Nome do arquivo .zip do plugin
PLUGIN_ZIP="anatelnews.zip"

# Diretório de destino para o arquivo .zip
DEST_DIR="$HOME/Downloads"

# Verifica se o diretório de destino existe
if [ ! -d "$DEST_DIR" ]; then
  echo "O diretório de destino não existe. Criando $DEST_DIR..."
  mkdir -p "$DEST_DIR"
fi

# Navegar para o diretório onde os arquivos do plugin estão localizados
cd "$LOCAL_PLUGIN_DIR" || {
  echo "Erro ao acessar o diretório $LOCAL_PLUGIN_DIR"
  exit 1
}

# Criar o arquivo .zip do plugin
echo "Criando arquivo .zip do plugin..."
zip -r "$PLUGIN_ZIP" ./*

# Mover o arquivo .zip para o diretório de downloads
echo "Movendo o arquivo .zip para $DEST_DIR..."
mv "$PLUGIN_ZIP" "$DEST_DIR"

echo "Implantação concluída com sucesso!"
