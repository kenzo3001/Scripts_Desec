#!/usr/bin/env python3
import argparse
import os
import re
import socket
import ssl
import sys
import time
from typing import Iterable, List, Tuple

def mostrar_demo() -> None:
    """Exibe uma demonstração rápida SEMPRE que o script for executado."""
    print("=== DEMO RÁPIDA ===")
    print("Objetivo: testar VRFY em um servidor SMTP para validar usuários.")
    print("\nExemplos de uso:")
    print("  1) Usuário único:")
    print("     python3 smtpenum.py 192.168.0.10 admin")
    print("  2) Lista de usuários a partir de arquivo:")
    print("     python3 smtpenum.py 192.168.0.10 users.txt")
    print("\nOpções úteis:")
    print("  --port 25            (padrão 25)")
    print("  --timeout 5          (padrão 5s)")
    print("  --starttls           (tenta STARTTLS após EHLO)")
    print("  --delay 0.2          (atraso entre consultas, em segundos)\n")
    print("Saídas esperadas:")
    print("  [250] Usuário válido           -> resposta positiva (existe)")
    print("  [252] Não confirma, aceita     -> pode indicar usuário provável")
    print("  [550] Usuário inexistente      -> resposta negativa\n")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enumeração de usuários via SMTP VRFY.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("ip", help="IP ou hostname do servidor SMTP")
    parser.add_argument("entrada", help="Usuário único OU caminho para arquivo .txt (um por linha)")
    parser.add_argument("--port", type=int, default=25, help="Porta do serviço SMTP")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout de conexão/leitura (s)")
    parser.add_argument("--starttls", action="store_true", help="Tentar STARTTLS após EHLO")
    parser.add_argument("--delay", type=float, default=0.0, help="Atraso entre VRFYs (s)")
    return parser.parse_args()

def carregar_usuarios(entrada: str) -> List[str]:
    """Aceita um usuário único ou um arquivo com um por linha."""
    if os.path.isfile(entrada):
        with open(entrada, "r", encoding="utf-8", errors="ignore") as f:
            usuarios = [ln.strip() for ln in f if ln.strip()]
        seen = set()
        dedup = []
        for u in usuarios:
            if u not in seen:
                dedup.append(u); seen.add(u)
        return dedup
    return [entrada.strip()]

def recv_line(sock: socket.socket, bufsize: int = 4096) -> str:
    """Lê uma resposta (linha) do servidor SMTP."""
    try:
        data = sock.recv(bufsize)
        return data.decode(errors="ignore").strip()
    except socket.timeout:
        return ""
    except Exception:
        return ""

def send_cmd(sock: socket.socket, cmd: str) -> str:
    sock.sendall(cmd.encode())
    return recv_line(sock)

def interpretar_resposta(resp: str) -> Tuple[int, str]:
    """Extrai código numérico e mensagem completa."""
    m = re.match(r"^(\d{3})[ -](.*)", resp, flags=re.S)
    if m:
        return int(m.group(1)), m.group(2).strip()
    return (-1, resp.strip())

def conectar_smtp(ip: str, port: int, timeout: float, starttls: bool) -> Tuple[socket.socket, str]:
    """Conecta e, opcionalmente, inicia STARTTLS."""
    sock = socket.create_connection((ip, port), timeout=timeout)
    sock.settimeout(timeout)

    banner = recv_line(sock)
    if not banner:
        raise RuntimeError("Sem banner do servidor (pode haver filtro ou timeout).")

    if starttls:
        ehlo = send_cmd(sock, "EHLO smtpenum.local\r\n")
        if "STARTTLS" not in ehlo.upper():
            extra = recv_line(sock)
            ehlo_full = f"{ehlo}\n{extra}".strip()
        else:
            ehlo_full = ehlo

        starttls_resp = send_cmd(sock, "STARTTLS\r\n")
        code, _ = interpretar_resposta(starttls_resp)
        if code != 220:
            raise RuntimeError(f"STARTTLS falhou: {starttls_resp}")

        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=ip)  # SNI se hostname
        send_cmd(sock, "EHLO smtpenum.local\r\n")

    return sock, banner

def vrfy(sock: socket.socket, user: str) -> Tuple[int, str]:
    resp = send_cmd(sock, f"VRFY {user}\r\n")
    return interpretar_resposta(resp)

def classificar(code: int) -> str:
    if code == 250:
        return "valido"
    if code == 252:
        return "provavel"
    if code == 550:
        return "inexistente"
    if code == -1:
        return "sem_resposta"
    return "desconhecido"

def main() -> None:
    mostrar_demo()

    if len(sys.argv) == 1:
        print("Uso: python3 smtpenum.py <IP> <usuario|arquivo.txt> [opções]\n")
        print("Dica: passe --help para ver todas as opções.")
        sys.exit(1)

    args = parse_args()

    try:
        usuarios = carregar_usuarios(args.entrada)
        if not usuarios:
            print("Nenhum usuário para testar.")
            sys.exit(1)
    except Exception as e:
        print(f"Erro ao carregar usuários: {e}")
        sys.exit(1)

    try:
        with conectar_smtp(args.ip, args.port, args.timeout, args.starttls) as sock:  

            print(f"\nConectado a {args.ip}:{args.port}")
            banner = recv_line(sock) 
            if not banner:
                pass
            else:
                print("Banner recebido:")
                print(banner)

            print("\nIniciando enumeração VRFY…\n")
            for user in usuarios:
                try:
                    code, msg = vrfy(sock, user)
                    status = classificar(code)
                    base = f"[{code if code != -1 else '---'}] Usuário: {user:<20} -> {msg}"
                    if status == "valido":
                        print(f"{base}\n   ✅ Encontrado (250).")
                    elif status == "provavel":
                        print(f"{base}\n   ⚠️  252 (não confirma, mas aceita) – pode indicar usuário provável.")
                    elif status == "inexistente":
                        print(f"{base}\n   ❌ Inexistente (550).")
                    elif status == "sem_resposta":
                        print(f"{base}\n   ⚠️  Sem resposta do servidor.")
                    else:
                        print(f"{base}\n   ℹ️  Código não mapeado.")
                    if args.delay > 0:
                        time.sleep(args.delay)
                except socket.timeout:
                    print(f"[---] Usuário: {user:<20} -> timeout ao consultar.")
                except Exception as e:
                    print(f"[ERR] Usuário: {user:<20} -> erro: {e}")

            try:
                send_cmd(sock, "QUIT\r\n")
            except Exception:
                pass

    except (socket.timeout, socket.gaierror) as e:
        print(f"Erro de rede: {e}")
        sys.exit(1)
    except ConnectionRefusedError:
        print("Conexão recusada. Verifique IP/porta/firewall.")
        sys.exit(1)
    except RuntimeError as e:
        print(f"Falha no protocolo: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
        sys.exit(130)

if __name__ == "__main__":
    main()
