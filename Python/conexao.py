import socket
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
    print("       🚀 CONEXÃO 🚀      ")
    print("=" * 50 + f"{RESET}\n")
    print("🔹 O script se conecta a um servidor na porta especificada e tenta autenticação.")
    print("🔹 Ele envia um usuário e uma senha e exibe as respostas do servidor.\n")
    print("🔹 Exemplo de uso:")
    print(f"   ➤ python3 script.py 192.168.1.1 21 admin 12345\n")
    print("🔹 Se as credenciais forem aceitas, a resposta do servidor será exibida.\n")
    time.sleep(3)

def validar_ip(ip):
    """Valida um endereço IP IPv4."""
    padrao_ip = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")
    if padrao_ip.match(ip):
        partes = ip.split(".")
        return all(0 <= int(parte) <= 255 for parte in partes)
    return False

def conectar(ip, porta, usuario, senha):
    """Conecta ao servidor e envia credenciais."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as meu_socket:
            meu_socket.settimeout(5)  
            print(f"\n🔍 {CYAN}Conectando a {ip}:{porta}...{RESET}")
            meu_socket.connect((ip, porta))

            banner = meu_socket.recv(1024).decode().strip()
            print(f"{GREEN}[+] Banner recebido:{RESET} {banner}")

            print(f"{CYAN}🔑 Enviando usuário: {usuario}{RESET}")
            meu_socket.sendall(f"USER {usuario}\r\n".encode())
            resposta = meu_socket.recv(1024).decode().strip()
            print(f"{YELLOW}[Resposta do servidor]{RESET} ➤ {resposta}")

            # Envia a senha
            print(f"{CYAN}🔑 Enviando senha: {senha}{RESET}")
            meu_socket.sendall(f"PASS {senha}\r\n".encode())
            resposta = meu_socket.recv(1024).decode().strip()
            print(f"{YELLOW}[Resposta do servidor]{RESET} ➤ {resposta}")

    except socket.timeout:
        print(f"{RED}Erro: Tempo de conexão esgotado.{RESET}")
    except ConnectionRefusedError:
        print(f"{RED}Erro: Conexão recusada em {ip}:{porta}.{RESET}")
    except socket.gaierror:
        print(f"{RED}Erro: Endereço IP inválido.{RESET}")
    except socket.error as e:
        print(f"{RED}Erro de socket: {e}{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Execução interrompida pelo usuário.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conectar a um servidor e enviar credenciais.")
    parser.add_argument("ip", help="Endereço IP do servidor")
    parser.add_argument("porta", type=int, help="Porta do servidor")
    parser.add_argument("usuario", help="Usuário para autenticação")
    parser.add_argument("senha", help="Senha para autenticação")

    args = parser.parse_args()

    mostrar_demo()  
    if not validar_ip(args.ip):
        print(f"{RED}Erro: Endereço IP inválido!{RESET}")
    elif args.porta < 1 or args.porta > 65535:
        print(f"{RED}Erro: Porta inválida! Escolha um número entre 1 e 65535.{RESET}")
    else:
        conectar(args.ip, args.porta, args.usuario, args.senha)
