#!/usr/bin/env python3
import sys
import socket
import argparse
import concurrent.futures
from contextlib import suppress

try:
    from tqdm import tqdm
    USE_TQDM = True
except ImportError:
    USE_TQDM = False

def mostrar_demo():
    print("\nDemonstração de uso:")
    print("python3 scanner.py 192.168.0.1")
    print("python3 scanner.py google.com --start 20 --end 100 --timeout 0.5 --threads 200")
    print("python3 scanner.py 10.0.0.1 --show-closed --resolve\n")

def _format_service_name(porta: int) -> str:
    with suppress(OSError):
        return socket.getservbyport(porta)
    return "Desconhecido"


def verifica_porta(host, porta, timeout, show_closed):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            code = s.connect_ex((host, porta))
            if code == 0:
                servico = _format_service_name(porta)
                print(f"\033[92m[ABERTA]\033[0m Porta {porta} ({servico})")
            elif show_closed:
                print(f"\033[91m[FECHADA]\033[0m Porta {porta}")
    except socket.timeout:
        if show_closed:
            print(f"\033[93m[TIMEOUT]\033[0m Porta {porta} - tempo limite excedido")
    except PermissionError:
        print(f"\033[91m[ERRO]\033[0m Permissão negada ao tentar acessar a porta {porta}.")
    except OSError as exc:
        # Erros de rede diferentes podem ocorrer (ex.: host inalcançável). Mostramos
        # a mensagem apenas quando o usuário deseja visualizar portas fechadas.
        if show_closed:
            print(f"\033[93m[ERRO]\033[0m Porta {porta}: {exc}")

def verifica_portas(host, start, end, timeout, threads, show_closed):
    print(f"\n🔎 Iniciando scan em {host} - Portas {start} a {end}\n")
    portas = range(start, end + 1)
    barra = tqdm(portas, desc="Verificando", unit="porta") if USE_TQDM else portas

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []

        for porta in barra:
            futures.append(executor.submit(verifica_porta, host, porta, timeout, show_closed))

        try:
            concurrent.futures.wait(futures)
        except KeyboardInterrupt:
            for future in futures:
                future.cancel()
            raise

def resolve_host(host):
    try:
        ip = socket.gethostbyname(host)
    except socket.gaierror as exc:
        print(f"\033[91m🚫 Falha ao resolver o host {host}: {exc}\033[0m")
        raise

    try:
        nome = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror):
        nome = host

    print(f"📌 IP Resolvido: {ip} ({nome})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scanner de portas simples com multithreading")
    parser.add_argument("host", nargs="?", help="Endereço IP ou hostname para escanear")
    parser.add_argument("--start", type=int, default=1, help="Porta inicial (padrão: 1)")
    parser.add_argument("--end", type=int, default=1024, help="Porta final (padrão: 1024)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Timeout por conexão em segundos (padrão: 1)")
    parser.add_argument("--threads", type=int, default=100, help="Número de threads simultâneas (padrão: 100)")
    parser.add_argument("--show-closed", action="store_true", help="Exibe também as portas fechadas")
    parser.add_argument("--resolve", action="store_true", help="Tenta resolver nome do host")
    parser.add_argument("--demo", action="store_true", help="Exibe exemplo de uso e sai")

    args = parser.parse_args()

    if args.demo:
        mostrar_demo()
        sys.exit(0)

    if not args.host:
        print("\033[91m🚫 Host não informado.\033[0m")
        mostrar_demo()
        sys.exit(1)

    if args.start < 1 or args.end > 65535 or args.start > args.end:
        print("\033[91mFaixa de portas inválida.\033[0m")
        sys.exit(1)

    try:
        socket.gethostbyname(args.host)
        if args.resolve:
            resolve_host(args.host)
        verifica_portas(args.host, args.start, args.end, args.timeout, args.threads, args.show_closed)
    except socket.gaierror:
        print(f"\033[91m🚫 Host inválido:\033[0m {args.host}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\033[93m🛑 Execução interrompida pelo usuário.\033[0m")
        sys.exit(0)
