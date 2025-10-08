#!/bin/bash

mostrar_demo() {
    echo "=========================================="
    echo "           🔍 DNS REVERSE 🔍             "
    echo "=========================================="
    echo "➡️  O script realiza uma busca reversa de DNS para um intervalo de IPs."
    echo "➡️  Ele tenta obter o nome associado a cada IP e exibe o resultado."
    echo "➡️  Exemplo de uso: $0 192.168.1 1 254"
    echo "------------------------------------------"
    sleep 3
}

if [ $# -ne 3 ]; then
    echo "❌ Uso incorreto!"
    echo "Modo correto: $0 <IP base> <intervalo inicial> <intervalo final>"
    exit 1
fi

BASE_IP=$1
START_RANGE=$2
END_RANGE=$3

if ! [[ "$START_RANGE" =~ ^[0-9]+$ ]] || ! [[ "$END_RANGE" =~ ^[0-9]+$ ]]; then
    echo "❌ Erro: O intervalo deve ser um número inteiro válido."
    exit 1
fi

if [ "$START_RANGE" -gt "$END_RANGE" ]; then
    echo "❌ Erro: O intervalo inicial deve ser menor ou igual ao intervalo final."
    exit 1
fi

mostrar_demo  

echo "🔎 Iniciando busca reversa de DNS em ${BASE_IP}.${START_RANGE} até ${BASE_IP}.${END_RANGE}..."
echo "------------------------------------------"

for ip in $(seq "$START_RANGE" "$END_RANGE"); do
    FULL_IP="${BASE_IP}.${ip}"
    REVERSE_DNS=$(host -t ptr "$FULL_IP" 2>/dev/null)

    if echo "$REVERSE_DNS" | grep -q "pointer"; then
        PTR_RECORD=$(echo "$REVERSE_DNS" | awk '{print $NF}')
        echo "✅ $FULL_IP → $PTR_RECORD"
    else
        echo "❌ $FULL_IP → Nenhum registro PTR encontrado"
    fi
done

echo "✅ Busca concluída!"
