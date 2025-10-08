import socket

def verifica_porta(ip, porta):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as meu_socket:
            meu_socket.settimeout(5)  # Definir um timeout para evitar longos tempos de espera
            conexao = meu_socket.connect_ex((ip, porta))

            if conexao == 0:
                print(f"Porta {porta} no IP {ip} está Aberta")
            else:
                print(f"Porta {porta} no IP {ip} está Fechada")
    except socket.timeout:
        print(f"Tempo de conexão esgotado ao verificar a porta {porta} em {ip}.")
    except OSError as erro:
        print(f"Erro ao verificar a porta {porta} em {ip}: {erro}")

if __name__ == "__main__":
    try:
        ip = input("Digite o IP: ")
        porta = int(input("Digite a porta: "))

        if porta < 1 or porta > 65535:
            raise ValueError("Porta inválida! Escolha um número entre 1 e 65535.")

        socket.gethostbyname(ip)  # Verifica se o IP é válido
        verifica_porta(ip, porta)

    except ValueError as e:
        print(f"Erro: {e}")
    except socket.gaierror:
        print("Endereço IP inválido.")
    except socket.timeout:
        print(f"Tempo de conexão esgotado para o IP {ip}.")
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
