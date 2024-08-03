#!/bin/bash

# Parar todos os containers
docker stop $(docker ps -aq)

# Remover todos os containers
docker rm $(docker ps -aq)

# Remover todas as imagens
docker rmi $(docker images -q)

# Remover todos os volumes
docker volume rm $(docker volume ls -q)

# Remover todas as redes que não são a padrão
docker network rm $(docker network ls | grep -v "bridge\|host\|none" | awk '/ / { print $1 }')

# Limpar volumes dangling
docker volume prune -f

# Limpar imagens dangling
docker image prune -f

# Limpar todas as networks
docker network prune -f

echo "Docker completamente limpo!"
