#!/bin/bash

mostrar_demo() {
    echo "=========================================="
    echo "             🔍 DNS ZONE 🔍              "
    echo "=========================================="
    echo "➡️  O script verifica servidores NS do domínio e tenta listar registros via transferência de zona (zone transfer)."
    echo "➡️  Exemplo de uso: $0 exemplo.com"
    echo "------------------------------------------"
    sleep 3
}

if [ -z "$1" ]; then
    echo "❌ Uso incorreto!"
    echo "Modo correto: $0 <URL>"
    exit 1
fi

URL=$1

mostrar_demo  

echo "🔎 Buscando servidores NS para $URL..."
NS_OUTPUT=$(host -t ns "$URL" | awk '{print $NF}')

if [ -z "$NS_OUTPUT" ]; then
    echo "❌ Nenhum servidor NS encontrado para $URL"
    exit 1
fi

echo "✅ Servidores NS encontrados:"
echo "$NS_OUTPUT"
echo "------------------------------------------"

for NS in $NS_OUTPUT; do
    echo "🔹 Tentando transferência de zona em $NS..."
    ZONE_TRANSFER=$(host -l "$URL" "$NS" 2>&1)

    if echo "$ZONE_TRANSFER" | grep -q "Transfer failed"; then
        echo "❌ Falha na transferência de zona para $NS"
    else
        echo "✅ Transferência de zona bem-sucedida em $NS:"
        echo "$ZONE_TRANSFER"
    fi
    echo "------------------------------------------"
done

echo "✅ Processo concluído!"
