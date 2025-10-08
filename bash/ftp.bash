#!/bin/bash
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"

HOST="$1"
PORT="${2:-21}"

if [[ -z "$HOST" ]]; then
    echo -e "${YELLOW}[!] Uso: $0 <host> [porta]${RESET}"
    exit 1
fi

echo -e "${CYAN}[+] Testando conexão FTP anônima em $HOST:$PORT...${RESET}"

RESPONSE=$(echo -e "user anonymous anonymous\nls\nquit" | timeout 6 ftp -inv "$HOST" "$PORT" 2>/dev/null)

if echo "$RESPONSE" | grep -q "230"; then
    echo -e "${GREEN}[+] Login anônimo bem-sucedido!${RESET}"
    echo -e "${YELLOW}[i] Listagem de arquivos:${RESET}"
    echo "$RESPONSE" | grep -A 999 "230"
elif echo "$RESPONSE" | grep -q "530"; then
    echo -e "${RED}[-] Login anônimo negado.${RESET}"
else
    echo -e "${RED}[-] Falha ao conectar ou resposta inesperada.${RESET}"
fi
