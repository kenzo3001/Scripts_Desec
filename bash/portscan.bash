#!/bin/bash

mostrar_demo() {
  echo -e "\n Demonstração de uso:"
  echo "  $0 <REDE_BASE>             → Escaneia as 100 portas mais comuns"
  echo "  $0 <REDE_BASE> <PORTA>     → Escaneia a porta específica"
  echo -e "    Exemplo: $0 192.168.0    ou    $0 192.168.0 22\n"
}

TOP_PORTS=(21 22 23 25 53 80 110 111 135 139 143 443 445 993 995 1723 3306 3389 5900 8080
  7 9 13 17 19 26 37 49 69 70 79 88 102 113 119 123 137 138 161 179 199 389 427 465 512
  513 514 515 520 546 547 554 587 636 873 902 989 990 993 995 1025 1080 1194 1214 1433
  1521 1720 1725 2049 2082 2083 2100 2222 2483 2484 3306 3389 3690 4444 4664 5000 5060
  5190 5222 5432 5500 5631 5632 5900 6000 6001 6660 6667 6697 7000 8000 8008 8080 8081
  8443 8888 9000 9090 10000)

if [ "$#" -lt 1 ]; then
  echo -e "\n Uso incorreto."
  echo "Modo de uso: $0 <REDE_BASE> [PORTA]"
  mostrar_demo
  exit 1
fi

REDE="$1"
PORTA="$2"

echo -e "\n Iniciando varredura em ${REDE}.0/24..."

for IP in {1..254}; do
  ALVO="${REDE}.${IP}"

  if [ -n "$PORTA" ]; then
    RESPONSE=$(hping3 -S -p "$PORTA" -c 1 "$ALVO" 2>/dev/null | grep "flags=SA")
    if [[ $RESPONSE != "" ]]; then
      echo -e "Porta $PORTA aberta em: \e[1;32m$ALVO\e[0m"
    fi
  else
    for p in "${TOP_PORTS[@]}"; do
      RESPONSE=$(hping3 -S -p "$p" -c 1 "$ALVO" 2>/dev/null | grep "flags=SA")
      if [[ $RESPONSE != "" ]]; then
        echo -e "Porta $p aberta em: \e[1;32m$ALVO\e[0m"
      fi
    done
  fi
done

echo -e "\n Varredura finalizada."
