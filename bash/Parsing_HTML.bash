#!/bin/bash

mostrar_demo() {
    echo "========================================="
    echo "          🌐 PARSING HTML 🌐            "
    echo "========================================="
    echo "➡️  O script baixa o HTML de um site e extrai os domínios contidos nele."
    echo "➡️  Depois, faz a resolução de IP para cada domínio encontrado."
    echo "➡️  Uso: $0 <site.com>"
    echo "➡️  Exemplo: $0 exemplo.com"
    echo "========================================="
    sleep 3
}

if [ -z "$1" ]; then
    echo "❌ Erro: Nenhum domínio fornecido!"
    echo "Modo correto: $0 <site.com>"
    exit 1
fi

SITE="$1"

mostrar_demo

echo "🔍 Baixando HTML de $SITE..."
HTML=$(curl -sL "$SITE")

DOMINIOS=$(echo "$HTML" | grep -Eo "https?://[^/\"']+" | sed -E 's#https?://##' | cut -d/ -f1 | sort -u)

if [ -z "$DOMINIOS" ]; then
    echo "❌ Nenhum domínio encontrado no HTML."
    exit 1
fi

echo "🌐 Domínios encontrados:" 
for d in $DOMINIOS; do
    IP=$(dig +short "$d" | head -n 1)
    if [ -n "$IP" ]; then
        echo "   $d -> $IP"
    else
        echo "   $d -> IP não encontrado"
    fi
done
