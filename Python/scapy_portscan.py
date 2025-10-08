#!/usr/bin/python3
import sys
from scapy.all import IP, TCP, sr, conf
from scapy.all import L3RawSocket  

def mostrar_demo():
    print("\nDemonstração do funcionamento do script:")
    print("Uso: python3 scan_ports.py <IP-alvo>")
    print("Exemplo: python3 scan_ports.py 192.168.1.1\n")

def escanear_portas(alvo):
    portas = [21, 22, 23, 25, 80, 110, 443]
    print(f"🔎 Escaneando {alvo} nas portas: {portas}\n")
    
    pacote_ip = IP(dst=alvo)
    pacote_tcp = TCP(dport=portas, flags="S")
    pacote = pacote_ip / pacote_tcp

    try:
        conf.L3socket = L3RawSocket 
        print("[🔄 DEBUG] Enviando pacotes SYN...")
        resp, _ = sr(pacote, timeout=2, verbose=0)
    except PermissionError:
        print("🚫 Permissão negada: execute o script com sudo.")
        sys.exit(1)

    if not resp:
        print("⚠️  Nenhuma resposta recebida. Verifique o firewall do destino.")
        return

    filtrar_resultados(resp)

def filtrar_resultados(respostas):
    print("📬 Resultados:\n")
    for envio, resposta in respostas:
        if resposta.haslayer(TCP):
            porta = resposta[TCP].sport
            flags = resposta[TCP].flags

            if flags == 0x12: 
                print(f"\033[1;32m✅ Porta {porta} ABERTA\033[0m")
            elif flags == 0x14:
                print(f"\033[1;31m❌ Porta {porta} FECHADA\033[0m")
            else:
                print(f"🟡 Porta {porta} retornou flags incomuns: {flags}")
        else:
            print("⚠️  Resposta recebida sem camada TCP.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso incorreto!")
        mostrar_demo()
        sys.exit(1)

    alvo = sys.argv[1]
    escanear_portas(alvo)
