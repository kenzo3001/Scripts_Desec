#!/bin/bash

mostrar_demo() {
    echo -e "\033[1;36m============================================\033[0m"
    echo -e "\033[1;33m🔍 SCRIPT DE VERIFICAÇÃO DE CNAME EM SUBDOMÍNIOS\033[0m"
    echo -e "\033[1;36m============================================\033[0m"
    echo -e "Este script verifica registros CNAME para subdomínios"
    echo -e "Entrada: Um arquivo .txt contendo uma palavra por linha (ex: www, mail, ftp)"
    echo -e "Domínio base: fornecido como segundo argumento (ex: exemplo.com)"
    echo -e "\033[1;36m============================================\033[0m"
    sleep 2
}

mostrar_uso() {
    echo "Uso: $0 <arquivo_txt> <domínio>"
    echo "Exemplo: $0 subdominios.txt exemplo.com"
    exit 1
}

verificar_cname() {
    local subdominio="$1.$2"
    local resultado1 resultado2

    resultado1=$(host -t cname "$subdominio" 2>/dev/null | awk '/alias for/ {print $NF}')
    if [ -n "$resultado1" ]; then
        resultado2=$(host -t cname "$resultado1" 2>/dev/null | awk '/alias for/ {print $NF}')
        echo -e "\033[1;32m$subdominio\033[0m → $resultado1 → ${resultado2:-N/A}"
    fi
}

[ "$#" -ne 2 ] && mostrar_uso

arquivo_txt="$1"
dominio="$2"

if [ ! -f "$arquivo_txt" ]; then
    echo -e "\033[1;31mErro:\033[0m Arquivo '$arquivo_txt' não encontrado."
    exit 1
fi

mostrar_demo

while IFS= read -r palavra || [ -n "$palavra" ]; do
    [[ -z "$palavra" || "$palavra" =~ ^# ]] && continue
    verificar_cname "$palavra" "$dominio"
done < "$arquivo_txt"
