import requests
import argparse
import time

# Cores para saída
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

security_headers = {
    "Strict-Transport-Security": "Protege contra ataques MITM e downgrade de protocolo.",
    "Content-Security-Policy": "Previne injeção de código malicioso (XSS).",
    "X-Content-Type-Options": "Evita que navegadores ignorem o tipo MIME declarado.",
    "X-Frame-Options": "Impede que o site seja incorporado em iframes (clickjacking).",
    "X-XSS-Protection": "Protege contra ataques de script entre sites (XSS).",
    "Referrer-Policy": "Controla o envio do cabeçalho Referer para proteger a privacidade.",
}

def mostrar_demo():
    """Exibe uma demonstração do funcionamento do script antes da execução."""
    print("=" * 50 + f"{RESET}")
    print("       🚀 CABEÇALHO DE SEGURANÇA 🚀      ")
    print("=" * 50 + f"{RESET}\n")
    print("🔹 O script verifica a presença de cabeçalhos de segurança em um site.")
    print("🔹 Se um cabeçalho estiver ausente, o site pode estar vulnerável.\n")
    print("🔹 Exemplo de saída:\n")
    print(f"   {GREEN}[+] Strict-Transport-Security: Encontrado{RESET}")
    print(f"   {RED}[-] X-Frame-Options: Não encontrado{RESET}\n")
    print("🔹 Recomendação: Ative todos os cabeçalhos de segurança no seu servidor.\n")
    time.sleep(3)

def verificar_cabecalhos_seguranca(url):
    """Verifica se os principais cabeçalhos de segurança estão presentes na resposta HTTP."""
    try:
        resposta = requests.get(url, timeout=5)
        headers = resposta.headers

        print(f"\n🔍 {CYAN}Verificando cabeçalhos de segurança para {url}...{RESET}\n")

        for header, descricao in security_headers.items():
            if header in headers:
                print(f"{GREEN}[+] {header}: Encontrado - {headers[header]}{RESET}")
            else:
                print(f"{RED}[-] {header}: Não encontrado{RESET} ❌")
                print(f"    {YELLOW}⚠️  {descricao}{RESET}")

    except requests.exceptions.Timeout:
        print(f"{RED}Erro: Tempo de conexão esgotado para {url}.{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}Erro ao acessar o site {url}: {e}{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verificar cabeçalhos de segurança de um site.")
    parser.add_argument("url", help="URL do site a ser verificado")
    args = parser.parse_args()


    mostrar_demo()

    if not args.url.startswith(('http://', 'https://')):
        args.url = 'http://' + args.url

    verificar_cabecalhos_seguranca(args.url)
