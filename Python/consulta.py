import socket
from whois import whois
import ipaddress
import argparse
import time
import re

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

def mostrar_demo():
    """Exibe uma demonstração do funcionamento do script antes da execução."""
    print(f"\n{CYAN}=" * 50)
    print("       🔍 CONSULTA 🔍       ")
    print("=" * 50 + f"{RESET}\n")
    print("🔹 O script consulta informações WHOIS de domínios e IPs.")
    print("🔹 Ele tenta identificar o servidor WHOIS correto e obter detalhes.")
    print("🔹 Caso a biblioteca `whois` falhe, ele tenta a consulta via socket.\n")
    print("🔹 Exemplo de uso:")
    print(f"   ➤ python3 script.py google.com")
    print(f"   ➤ python3 script.py 8.8.8.8\n")
    time.sleep(3)

def is_ip(address):
    """Verifica se o endereço é um IP (IPv4 ou IPv6)."""
    try:
        ipaddress.ip_address(address)
        return True
    except ValueError:
        return False

def validar_dominio(dominio):
    """Valida um nome de domínio usando regex."""
    padrao = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
    return bool(padrao.match(dominio))

def query_whois_via_socket(address):
    """Consulta WHOIS usando sockets para IPs ou domínios."""
    try:
        print(f"{CYAN}🔍 Conectando ao WHOIS da IANA para obter servidor WHOIS...{RESET}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect(("whois.iana.org", 43))
            s.sendall(f"{address}\r\n".encode("utf-8"))
            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
        response_decoded = response.decode("utf-8")

        whois_server = None
        for line in response_decoded.splitlines():
            if line.lower().startswith("refer:" ):
                whois_server = line.split(":", 1)[1].strip()
                break

        if not whois_server:
            print(f"{RED}Erro: Nenhum servidor WHOIS encontrado na resposta da IANA.{RESET}")
            return

        print(f"{GREEN}✅ Servidor WHOIS encontrado: {whois_server}{RESET}")

        print(f"{CYAN}🔍 Consultando WHOIS em {whois_server}...{RESET}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
            s1.settimeout(5)
            s1.connect((whois_server, 43))
            s1.sendall(f"{address}\r\n".encode("utf-8"))
            detailed_response = b""
            while True:
                data = s1.recv(4096)
                if not data:
                    break
                detailed_response += data
        print(f"{GREEN}✅ Resposta WHOIS recebida:{RESET}\n")
        print(detailed_response.decode("utf-8"))

    except socket.timeout:
        print(f"{RED}Erro: Tempo de conexão esgotado.{RESET}")
    except Exception as e:
        print(f"{RED}Erro ao realizar consulta WHOIS via socket: {e}{RESET}")

def query_whois(address):
    """Realiza a consulta WHOIS para um host, IPv4 ou IPv6."""
    if is_ip(address):
        print(f"{YELLOW}🌐 Realizando consulta WHOIS para IP: {address}{RESET}")
        query_whois_via_socket(address)
    elif validar_dominio(address):
        try:
            print(f"{YELLOW}🌍 Realizando consulta WHOIS para domínio: {address}{RESET}")
            domain_info = whois(address)
            print(f"{GREEN}✅ Informações WHOIS do domínio:{RESET}")
            print(domain_info)
        except Exception as e:
            print(f"{RED}Erro ao consultar WHOIS via biblioteca: {e}{RESET}")
            print(f"{CYAN}Tentando consulta via socket...{RESET}")
            query_whois_via_socket(address)
    else:
        print(f"{RED}Erro: Endereço inválido! Insira um IP ou domínio válido.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consulta WHOIS para host, IPv4 ou IPv6.")
    parser.add_argument("address", type=str, help="Host, IPv4 ou IPv6 a ser consultado")
    args = parser.parse_args()

    mostrar_demo()  
    query_whois(args.address)
