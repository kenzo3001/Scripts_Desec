import os, sys, argparse, configparser, textwrap, datetime as dt
from typing import List, Union, BinaryIO
from io import BytesIO
from tqdm import tqdm
from tenable.nessus import Nessus
import re

# ---------------------------- Config ----------------------------
DEFAULT_CFG, DEFAULT_SEC = 'config.txt', 'nessus'
cli = argparse.ArgumentParser(description='Baixa relatórios de scans do Nessus.')
cli.add_argument('--config', default=DEFAULT_CFG)
cli.add_argument('--profile', default=DEFAULT_SEC)
cli.add_argument('--formats')
args = cli.parse_args()

cfg = configparser.ConfigParser()
if not cfg.read(args.config, encoding='utf-8'):
    sys.exit(f"Arquivo '{args.config}' não encontrado.")
if args.profile not in cfg:
    sys.exit(f"Seção '{args.profile}' ausente no INI.")

c = cfg[args.profile]
getbool = lambda k, d=False: c.get(k, str(d)).lower() in {'1','true','yes'}
BASE_URL   = c.get('base_url'); VERIFY_SSL = getbool('verify_ssl')
FOLDER_ID  = c.getint('folder_id'); DEST_DIR = c.get('dest_dir','output')
TIMEOUT    = c.getint('timeout',120); CHUNK_SZ = c.getint('chunk_sz',65536)
username   = c.get('username','');   password   = c.get('password','')
access_key = c.get('access_key',''); secret_key = c.get('secret_key','')

if access_key and secret_key:
    nessus = Nessus(url=BASE_URL, access_key=access_key, secret_key=secret_key,
                    verify=VERIFY_SSL, timeout=TIMEOUT)
elif username and password:
    nessus = Nessus(url=BASE_URL, username=username, password=password,
                    verify=VERIFY_SSL, timeout=TIMEOUT)
else:
    sys.exit('Defina username/password ou access_key/secret_key')

SUPPORTED = {
    'nessus': {'ext': '.nessus', 'kwargs': {}},
    'csv':    {'ext': '.csv',    'kwargs': {'format': 'csv'}},
    'pdf':    {'ext': '.pdf',    'kwargs': {'format': 'pdf', 'chapters':['vuln_hosts_summary']}},
    'html':   {'ext': '.html',   'kwargs': {'format': 'html','chapters':['vuln_hosts_summary']}},
}

WIN_RESERVED = {
    'CON','PRN','AUX','NUL',
    *(f'COM{i}' for i in range(1,10)),
    *(f'LPT{i}' for i in range(1,10)),
}

def safe_filename(name: str, maxlen: int = 160) -> str:
    name = (name or "").strip()

    # 1) remove caracteres de controle (inclui \t \n \r etc.)
    name = re.sub(r'[\x00-\x1f]', '_', name)

    # 2) remove caracteres proibidos no Windows
    name = re.sub(r'[<>:"/\\|?*]', '_', name)

    # 3) normaliza espaços
    name = re.sub(r'\s+', '_', name)

    # 4) Windows não aceita terminar com espaço ou ponto
    name = name.rstrip(' .')

    # 5) evita nomes reservados
    if name.upper() in WIN_RESERVED:
        name = '_' + name

    # 6) evita nome vazio e controla tamanho
    name = name[:maxlen].rstrip(' .')
    return name or 'scan'

def prompt() -> List[str]:
    msg=textwrap.dedent('''\nFormatos: 1) nessus 2) csv 3) pdf 4) html 5) todos 0) sair''')
    print(msg); m={'1':['nessus'],'2':['csv'],'3':['pdf'],'4':['html'],'5':list(SUPPORTED),'0':[]}
    sel=m.get(input('Opção: ').strip(),'x');
    if sel=='x': sys.exit('Opção inválida.');
    if not sel: sys.exit(0); return sel
    return sel

formats=[f.strip().lower() for f in (args.formats or '').split(',') if f] or prompt()
for f in formats:
    if f not in SUPPORTED: sys.exit(f'Formato inválido: {f}')

os.makedirs(DEST_DIR, exist_ok=True)

scans=nessus.scans.list(folder_id=FOLDER_ID)
scans=scans.get('scans',[]) if isinstance(scans,dict) else scans
if not scans: sys.exit('Nenhum scan na pasta.')

def flatten_csv(p:str):
    tmp=p+'.tmp'
    with open(p,'r',encoding='utf-8',errors='ignore') as src, open(tmp,'w',encoding='utf-8',newline='') as dst:
        in_q=False
        while (ch:=src.read(1)):
            if ch=='"': in_q=not in_q; dst.write(ch)
            elif ch in {'\n','\r'} and in_q: dst.write(' ')
            else: dst.write(ch)
    os.replace(tmp,p)

def latest_history(sid:int):
    h=nessus.scans.details(sid).get('history',[])
    if not h: return None,None
    latest=max(h,key=lambda x:x.get('last_modification_date',x.get('history_id',0)))
    hid=latest['history_id']; epoch=latest.get('last_modification_date') or latest.get('creation_date')
    return hid, epoch or 0

# download loop
for sc in scans:
    sid=sc['id']; name = safe_filename(sc.get('name', ''))
    hid, epoch=latest_history(sid); hid=hid or 0
    for fmt in formats:
        ext=SUPPORTED[fmt]['ext']
        outfile=os.path.join(DEST_DIR,f"{name}_{sid}_{hid}_{epoch}{ext}")
        if os.path.exists(outfile):
            print('[SKIP]',os.path.basename(outfile)); continue
        print(f'[+] {name} → {fmt}')
        try:
            data=nessus.scans.export_scan(sid,**SUPPORTED[fmt]['kwargs'])
            # save
            if isinstance(data,(bytes,bytearray)):
                with open(outfile,'wb') as f: f.write(data)
            else:
                with open(outfile,'wb') as f:
                    while chunk:=data.read(CHUNK_SZ): f.write(chunk)
                if hasattr(data,'close'): data.close()
            if fmt=='csv': flatten_csv(outfile)
            print('[✔]',os.path.basename(outfile))
        except Exception as e:
            print('[ERRO]',name,fmt,e)
