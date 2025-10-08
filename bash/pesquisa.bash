#!/bin/bash

mostrar_demo() {
    echo "========================================="
    echo " 🔍 Script de Busca no Google (Lynx) 🔍 "
    echo "========================================="
    echo "➡️  O script pesquisa arquivos com uma determinada extensão."
    echo "➡️  Ele busca no Google usando o Lynx e extrai as URLs."
    echo "➡️  Exemplo: $0 exemplo.com pdf"
    echo "========================================="
    sleep 2
}

mostrar_uso() {
    echo "Uso: $0 <domínio> <extensão>"
    echo "Exemplo: $0 exemplo.com pdf"
    exit 1
}

mostrar_demo

if [ -z "$1" ] || [ -z "$2" ]; then
    mostrar_uso
fi

DOMINIO=$1
EXTENSAO=$2

if ! command -v lynx &>/dev/null; then
    echo "❌ Erro: O Lynx não está instalado. Instale com 'sudo apt install lynx' ou equivalente."
    exit 1
fi

echo "🔎 Buscando arquivos .$EXTENSAO no domínio $DOMINIO..."
sleep 2

lynx --dump "http://www.google.com/search?num=500&q=site:$DOMINIO+ext:$EXTENSAO" -useragent="Mozilla/5.0" | \
    grep -Eo "https?://[^ ]+\.$EXTENSAO" | \
    sort -u > resultados.txt


if [ -s resultados.txt ]; then
    echo "✅ URLs encontradas:"
    cat resultados.txt
else
    echo "❌ Nenhuma URL encontrada para '$DOMINIO' com a extensão '$EXTENSAO'."
    rm -f resultados.txt
fi
