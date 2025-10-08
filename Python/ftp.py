#!/usr/bin/env python3
import ftplib
import argparse
import socket
import sys

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

def conectar_ftp_anonimo(host, porta):
    try:
        print(f"{CYAN}[+] Conectando ao FTP {host}:{porta}...{RESET}")
        ftp = ftplib.FTP()
        ftp.connect(host, porta, timeout=5)
        ftp.login()  # como anonymous por padrão
        print(f"{GREEN}[+] Sucesso: Login como 'anonymous' permitido!{RESET}")
        print(f"{YELLOW}[i] Diretório raiz listado abaixo:{RESET}")
        try:
            arquivos = ftp.nlst()
            for arq in arquivos:
                print(f"  - {arq}")
        except ftplib.error_perm:
            print(f"{RED}[-] Sem permissão para listar diretório.{RESET}")
        ftp.quit()
    except (socket.gaierror, socket.timeout):
        print(f"{RED}[-] Erro de rede: host {host} não encontrado ou inacessível.{RESET}")
    except ftplib.error_perm as e:
        print(f"{RED}[-] Permissão negada: {e}{RESET}")
    except ftplib.all_errors as e:
        print(f"{RED}[-] Erro de conexão FTP: {e}{RESET}")
    except Exception as e:
        print(f"{RED}[-] Erro inesperado: {e}{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tenta login anônimo em servidor FTP.")
    parser.add_argument("host", help="Endereço IP ou hostname do servidor FTP")
    parser.add_argument("--porta", "-p", type=int, default=21, help="Porta FTP (padrão: 21)")
    args = parser.parse_args()

    conectar_ftp_anonimo(args.host, args.porta)
