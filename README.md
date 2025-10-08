# 🛠️ Scripts de Pentest

Coleção de scripts para **segurança ofensiva**, **reconhecimento**, **enumeração** e **varredura**. O foco é praticidade, padronização de saída e automação para uso em laboratório e avaliações autorizadas.

[Instalação](#instalação) •
[Categorias](#categorias) •
[Uso rápido](#uso-rápido) •
[Scripts](#scripts) •
[Roadmap](#roadmap) •
[Contribuindo](#contribuindo) •
[Segurança & Ética](#segurança--ética) •
[Licença](#licença)

---

## 📚 Categorias

- **Reconhecimento**: banner grabbing, DNS, metadados, web recon.
- **Varredura/Enumeração**: port scan (Bash, Python, scapy, C), enum SMTP, FTP.
- **Utilitários**: parsing HTML, pesquisa/grep, port knocking, sockets em C.

> Linguagens presentes: Python, Shell, C e PowerShell.  

---

## ⚙️ Instalação

Dependências variam por script. Exemplos:

```bash
# Python
python3 --version

# Bash (exemplos)
sudo apt-get update && sudo apt-get install -y nmap jq dnsutils curl

# PowerShell (opcional)
pwsh --version

# C (exemplos)
gcc -O2 -o dns_resolver dns_resolver.c