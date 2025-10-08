#!/bin/bash

# Cores para saída
VERDE="\e[32m"
VERMELHO="\e[31m"
AZUL="\e[34m"
RESET="\e[0m"

mostrar_demo() {
    echo -e "${AZUL}========================================"
    echo -e "               🔍 DISCOVERY 🔍                "
    echo -e "========================================${RESET}"
    echo -e "🛜 O script varre um intervalo de IPs e exibe quais estão ativos."
    echo -e "🔹 Ele envia pacotes ICMP e filtra respostas válidas."
    echo -e "🔹 Para evitar travamentos, a varredura roda em paralelo."
    echo -e "🔹 Exemplo de uso:"
    echo -e "   ➤ ${VERDE}$0 192.168.1${RESET}\n"
    sleep 3
}

if [ -z "$1" ]; then
    echo -e "${VERMELHO}Modo de uso: $0 <rede_base>${RESET}"
    echo -e "Exemplo: $0 192.168.0"
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${VERMELHO}Erro: Formato de rede inválido! Use algo como 192.168.1${RESET}"
    exit 1
fi

mostrar_demo  

echo -e "${AZUL}🔍 Iniciando varredura em $1.0/24...${RESET}"
echo -e "${AZUL}------------------------------------${RESET}"


for host in {1..254}; do
    (
        ip="$1.$host"
        if ping -c 1 -W 1 "$ip" | grep -q "64 bytes"; then
            echo -e "${VERDE}[+] Host ativo: $ip${RESET}"
        fi
    ) &
done

wait

echo -e "${AZUL}✅ Varredura concluída.${RESET}"
