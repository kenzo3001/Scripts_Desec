#!/usr/bin/env python3
"""
download_PowerBI.py

Automatiza a extracao de dados do Tenable (Tenable One / Tenable.io) e grava
CSVs prontos para o Power BI na pasta indicada. Suporta tres modulos:
    - VM    (Vulnerability Management)  -> Export API assincrona
    - WAS   (Web App Scanning)          -> Export API assincrona (mesmo padrao)
    - CLOUD (Cloud Security)            -> API GraphQL paginada por cursor

Gera UM CSV por modulo (os schemas sao diferentes demais para um arquivo so).

Uso:
    python download_PowerBI.py --pasta caminho/desejado --config cliente_A.txt
    python download_PowerBI.py --pasta caminho/desejado --config cliente_A.txt --snapshot
"""

import argparse
import csv
import os
import sys
import time
import datetime
import json
import requests


# ---------------------------------------------------------------------------
# 1. Argumentos de linha de comando
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Extrai dados do Tenable (VM, WAS, Cloud) para o Power BI."
    )
    parser.add_argument(
        "--pasta",
        required=True,
        help="Pasta de destino dos CSVs (ex: a pasta do SharePoint sincronizada).",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Arquivo de configuracao com as chaves do cliente (ex: cliente_A.txt).",
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="Se presente, adiciona a data no nome dos arquivos (para historico).",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# 2. Leitura do arquivo de configuracao (formato chave=valor)
# ---------------------------------------------------------------------------
def carregar_config(caminho_config):
    """
    Formato do arquivo .txt (linhas com # sao comentarios):

        # Quais modulos rodar (separados por virgula): vm, was, cloud
        modulos=vm,was,cloud

        # --- Credenciais VM e WAS (X-ApiKeys) ---
        access_key=SUA_ACCESS_KEY
        secret_key=SUA_SECRET_KEY
        base_url=https://cloud.tenable.com

        # --- Cloud Security (GraphQL) ---
        # O endpoint e o token saem do console de Cloud Security do cliente.
        cloud_graphql_url=https://COLE_AQUI_O_ENDPOINT/graphql
        cloud_token=COLE_AQUI_O_BEARER_TOKEN

        # --- Geral ---
        nome_cliente=Cliente_A
        chunk_size=5000
    """
    if not os.path.isfile(caminho_config):
        sys.exit(f"[ERRO] Arquivo de config nao encontrado: {caminho_config}")

    config = {}
    with open(caminho_config, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            config[chave.strip()] = valor.strip()

    # Valores padrao
    config.setdefault("base_url", "https://cloud.tenable.com")
    config.setdefault("nome_cliente", "cliente")
    config.setdefault("chunk_size", "5000")
    config.setdefault("modulos", "vm")  # por padrao so VM

    # Normaliza a lista de modulos
    config["modulos"] = [
        m.strip().lower() for m in config["modulos"].split(",") if m.strip()
    ]

    # Validacao condicional das credenciais
    precisa_apikeys = any(m in config["modulos"] for m in ("vm", "was"))
    if precisa_apikeys:
        for c in ("access_key", "secret_key"):
            if c not in config:
                sys.exit(f"[ERRO] Modulo VM/WAS exige '{c}' no config.")

    if "cloud" in config["modulos"]:
        for c in ("cloud_graphql_url", "cloud_token"):
            if c not in config:
                sys.exit(f"[ERRO] Modulo cloud exige '{c}' no config.")

    # Filtros opcionais dos exports de VM e WAS (objeto JSON em UMA linha cada).
    # Ex.: vm_filters={"severity": ["critical", "high"], "state": ["OPEN", "REOPENED"]}
    #      was_filters={"severity": ["medium", "high", "critical"]}
    for modulo in ("vm", "was"):
        chave_filtros = f"{modulo}_filters"
        if config.get(chave_filtros):
            try:
                config[chave_filtros] = json.loads(config[chave_filtros])
            except json.JSONDecodeError as e:
                sys.exit(f"[ERRO] {chave_filtros} nao e um JSON valido: {e}")
        else:
            config[chave_filtros] = {}

        # Conveniencia: <modulo>_since_days=N injeta o filtro 'since' (N dias atras)
        # sem voce precisar calcular o timestamp Unix na mao.
        chave_dias = f"{modulo}_since_days"
        if config.get(chave_dias):
            try:
                dias = int(config[chave_dias])
                corte = datetime.datetime.now() - datetime.timedelta(days=dias)
                config[chave_filtros]["since"] = int(corte.timestamp())
            except ValueError:
                sys.exit(f"[ERRO] {chave_dias} deve ser um numero inteiro.")

    return config


# ---------------------------------------------------------------------------
# 3. Cabecalho de autenticacao VM/WAS
# ---------------------------------------------------------------------------
def montar_headers(config):
    return {
        "X-ApiKeys": f"accessKey={config['access_key']};secretKey={config['secret_key']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        # User-Agent recomendado pela Tenable para identificar a integracao
        "User-Agent": "PowerBI-Export-Consultoria/1.0",
    }


# ---------------------------------------------------------------------------
# 4. Export assincrono generico (serve para VM e WAS - mesmo fluxo)
#    Diferenca: o caminho base. VM=/vulns/export  WAS=/was/v1/export/vulns
# ---------------------------------------------------------------------------
def exportar_async(config, headers, caminho_base, rotulo, num_assets, filtros=None):
    base_url = config["base_url"].rstrip("/")
    url_export = f"{base_url}{caminho_base}"

    # 4.1 Dispara o export
    print(f"[INFO] Disparando export {rotulo}...")
    payload = {"num_assets": num_assets}
    if filtros:
        payload["filters"] = filtros
        print(f"[INFO] {rotulo}: filtros aplicados -> {filtros}")
    resp = requests.post(url_export, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    export_uuid = resp.json()["export_uuid"]
    print(f"[INFO] {rotulo} export_uuid: {export_uuid}")

    # 4.2 Polling + download dos chunks
    chunks_processados = set()
    dados = []

    while True:
        status_resp = requests.get(
            f"{url_export}/{export_uuid}/status", headers=headers, timeout=60
        )
        status_resp.raise_for_status()
        info = status_resp.json()
        status = info.get("status")
        disponiveis = set(info.get("chunks_available", []))

        for chunk_id in sorted(disponiveis - chunks_processados):
            print(f"[INFO] {rotulo}: baixando chunk {chunk_id}...")
            chunk_resp = requests.get(
                f"{url_export}/{export_uuid}/chunks/{chunk_id}",
                headers=headers,
                timeout=120,
            )
            chunk_resp.raise_for_status()
            registros = chunk_resp.json()
            dados.extend(registros)
            chunks_processados.add(chunk_id)
            print(f"[INFO] {rotulo}: chunk {chunk_id} -> {len(registros)} registros.")

        if status == "FINISHED" and disponiveis == chunks_processados:
            break
        if status == "ERROR":
            sys.exit(f"[ERRO] {rotulo}: o Tenable retornou status ERROR.")

        print(f"[INFO] {rotulo}: status {status}. Aguardando proximos chunks...")
        time.sleep(15)

    print(f"[INFO] {rotulo}: total de {len(dados)} registros.")
    return dados


def exportar_vm(config, headers):
    # VM: num_assets define o tamanho do chunk (1000-5000 e razoavel)
    num = int(config["chunk_size"])
    filtros = config.get("vm_filters") or None
    return exportar_async(config, headers, "/vulns/export", "VM", num, filtros)


def exportar_was(config, headers):
    # WAS: num_assets default 50, maximo 5000; a Tenable recomenda 1000-3000.
    num = min(int(config.get("chunk_size", "3000")), 5000)
    num = max(num, 1000)
    filtros = config.get("was_filters") or None
    return exportar_async(config, headers, "/was/v1/export/vulns", "WAS", num, filtros)


# ---------------------------------------------------------------------------
# 5. Cloud Security (GraphQL paginado por cursor)
#    ATENCAO: endpoint e token saem do console de Cloud Security do cliente.
#    Pode exigir validacao de parceiro junto a Tenable para retornar dados.
# ---------------------------------------------------------------------------
def exportar_cloud(config):
    url = config["cloud_graphql_url"]
    headers = {
        "Authorization": f"Bearer {config['cloud_token']}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "PowerBI-Export-Consultoria/1.0",
    }

    # Query de instancias de vulnerabilidade (limite de paginacao: 10.000).
    # 'first' e 'after' fazem a paginacao por cursor.
    query = """
    query ($first: Int!, $after: String) {
      VulnerabilityInstances(first: $first, after: $after) {
        nodes {
          FirstScanTime
          ResolutionTime
          Resolved
          Software { Name }
          Resource { Id Name }
          Vulnerability { Id Severity CvssScore Description }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
    """

    dados = []
    cursor = None
    pagina = 0

    while True:
        pagina += 1
        variables = {"first": 100, "after": cursor}
        resp = requests.post(
            url,
            json={"query": query, "variables": variables},
            headers=headers,
            timeout=120,
        )
        resp.raise_for_status()
        body = resp.json()

        if "errors" in body:
            sys.exit(f"[ERRO] CLOUD (GraphQL): {body['errors']}")

        bloco = body["data"]["VulnerabilityInstances"]
        nodes = bloco.get("nodes", [])
        dados.extend(nodes)
        print(f"[INFO] CLOUD: pagina {pagina} -> {len(nodes)} registros.")

        page_info = bloco.get("pageInfo", {})
        if page_info.get("hasNextPage"):
            cursor = page_info.get("endCursor")
            time.sleep(1)  # respeita rate limit
        else:
            break

    print(f"[INFO] CLOUD: total de {len(dados)} registros.")
    return dados


# ---------------------------------------------------------------------------
# 6. Achatamento do JSON aninhado e gravacao em CSV
# ---------------------------------------------------------------------------
def achatar(registro, prefixo="", resultado=None):
    if resultado is None:
        resultado = {}
    for chave, valor in registro.items():
        nova_chave = f"{prefixo}{chave}"
        if isinstance(valor, dict):
            achatar(valor, prefixo=f"{nova_chave}.", resultado=resultado)
        elif isinstance(valor, list):
            resultado[nova_chave] = "; ".join(str(item) for item in valor)
        else:
            resultado[nova_chave] = valor
    return resultado


def gravar_csv(dados, caminho_arquivo, rotulo):
    if not dados:
        print(f"[AVISO] {rotulo}: nenhum dado para gravar (CSV nao criado).")
        return

    linhas = [achatar(reg) for reg in dados]
    colunas = sorted({c for linha in linhas for c in linha.keys()})

    with open(caminho_arquivo, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(linhas)

    print(f"[OK] {rotulo}: CSV gravado em {caminho_arquivo}")


# ---------------------------------------------------------------------------
# 7. Funcao principal
# ---------------------------------------------------------------------------
def main():
    args = parse_args()

    if not os.path.isdir(args.pasta):
        sys.exit(f"[ERRO] Pasta de destino nao existe: {args.pasta}")

    config = carregar_config(args.config)
    nome_cliente = config["nome_cliente"]
    modulos = config["modulos"]

    # Sufixo de data para historico (--snapshot)
    sufixo = f"_{datetime.date.today().isoformat()}" if args.snapshot else ""

    def caminho(modulo):
        return os.path.join(args.pasta, f"{nome_cliente}_{modulo}{sufixo}.csv")

    # Credenciais X-ApiKeys so sao montadas se VM ou WAS estiverem ativos
    headers = montar_headers(config) if ({"vm", "was"} & set(modulos)) else None

    if "vm" in modulos:
        gravar_csv(exportar_vm(config, headers), caminho("vulns_vm"), "VM")

    if "was" in modulos:
        gravar_csv(exportar_was(config, headers), caminho("vulns_was"), "WAS")

    if "cloud" in modulos:
        gravar_csv(exportar_cloud(config), caminho("vulns_cloud"), "CLOUD")

    print("[FIM] Extracao concluida.")


if __name__ == "__main__":
    main()