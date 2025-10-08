#!/bin/bash

# Cores para saída
RED="\e[31m"
GREEN="\e[32m"
YELLOW="\e[33m"
CYAN="\e[36m"
RESET="\e[0m"

mostrar_uso() {
    echo -e "${YELLOW}Uso: $0 -u <URL base> -w <arquivo de lista> [-e <extensão>]${RESET}"
    echo -e "${CYAN}Exemplo:${RESET} $0 -u http://exemplo.com -w minha_lista.txt -e html"
    echo -e "${CYAN}Para não buscar arquivos específicos, omita a opção '-e'${RESET}"
    exit 1
}

mostrar_demo() {
    clear
    echo -e "${CYAN}"
    echo "============================================="
    echo "            🚀 WEB RECON 🚀                 "
    echo "============================================="
    echo -e "${RESET}"
    echo "🔹 O script tentará acessar diretórios e arquivos com base em um arquivo de lista."
    echo "🔹 Ele verifica a existência de URLs e exibe respostas HTTP."
    echo "🔹 Resultados bem-sucedidos serão destacados."
    echo ""
    echo -e "${CYAN}Exemplo:${RESET}"
    echo ""
    echo "   ➤ Verificando: http://site.com/admin/  [HTTP 200 ✅]"
    echo "   ➤ Verificando: http://site.com/backup.zip  [HTTP 404 ❌]"
    echo ""
    echo "🔹 Você pode interromper a execução com CTRL + C."
    echo ""
    sleep 3
}

verificar_url() {
    local url=$1
    local status=$(curl -s -A "Mozilla/5.0" -o /dev/null -w "%{http_code}" "$url")
    echo "$status"
}

log_acao() {
    local mensagem=$1
    local tipo=$2
    local status_code=$3
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")

    case $tipo in
        "INFO") cor=$CYAN ;;
        "ERRO") cor=$RED ;;
        "SUCESSO") cor=$GREEN ;;
        *) cor=$RESET ;;
    esac

    echo -e "${cor}[$tipo] [$timestamp] $mensagem (HTTP: $status_code)${RESET}"
}

# Processamento de argumentos
while getopts "u:w:e:" opt; do
    case "$opt" in
        u) URL_BASE="$OPTARG" ;;
        w) ARQUIVO_LISTA="$OPTARG" ;;
        e) EXTENSAO="$OPTARG" ;;
        *) mostrar_uso ;;
    esac
done

# Verifica se os argumentos essenciais foram fornecidos
if [[ -z "$URL_BASE" || -z "$ARQUIVO_LISTA" ]]; then
    mostrar_uso
fi

# Mostra a demonstração antes de iniciar
mostrar_demo

# Verifica se o arquivo de lista existe
if [[ ! -f "$ARQUIVO_LISTA" ]]; then
    log_acao "Arquivo '$ARQUIVO_LISTA' não encontrado." "ERRO" "N/A"
    exit 1
fi

# Verifica se o host está acessível
log_acao "Testando conectividade com $URL_BASE" "INFO" "N/A"
if ! curl -s --head "$URL_BASE" | grep "HTTP/" >/dev/null; then
    log_acao "Host inacessível ou inválido: $URL_BASE" "ERRO" "N/A"
    exit 1
fi

log_acao "Iniciando varredura no URL base: $URL_BASE" "INFO" "N/A"

processar_palavra() {
    local palavra=$1
    local url_base=$2
    local extensao=$3

    local url_diretorio="$url_base/$palavra/"
    local status_diretorio=$(verificar_url "$url_diretorio")

    if [[ "$status_diretorio" == "200" ]]; then
        log_acao "Diretório encontrado: $url_diretorio" "SUCESSO" "$status_diretorio"
    fi

    if [[ -n "$extensao" ]]; then
        local url_arquivo="$url_base/$palavra.$extensao"
        local status_arquivo=$(verificar_url "$url_arquivo")
        
        if [[ "$status_arquivo" == "200" ]]; then
            log_acao "Arquivo encontrado: $url_arquivo" "SUCESSO" "$status_arquivo"
        fi
    fi
}

export -f processar_palavra verificar_url log_acao

cat "$ARQUIVO_LISTA" | xargs -I{} -P 10 bash -c 'processar_palavra "$1" "$2" "$3"' _ {} "$URL_BASE" "$EXTENSAO"

log_acao "Varredura concluída." "INFO" "N/A"
