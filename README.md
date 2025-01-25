# Anatel News Integrator

Este projeto, "Anatel News Integrator", é uma ferramenta desenvolvida em Python que automatiza a coleta de notícias do site da Anatel para popular um blog. Este script busca as últimas notícias e as publica de forma organizada.

## Como Funciona

O integrador acessa a API pública da Anatel (ou coleta dados diretamente do site, se aplicável), extrai as notícias e as formata para serem postadas automaticamente no blog.

## Pré-requisitos

Para executar este projeto, você precisará ter Python instalado em sua máquina. Além disso, algumas bibliotecas externas são necessárias:
- `requests`: Para fazer chamadas HTTP.
- `beautifulsoup4`: Para fazer o parsing de HTML.

Você pode instalar todas as dependências necessárias com o seguinte comando:

```bash
pip install requests beautifulsoup4
