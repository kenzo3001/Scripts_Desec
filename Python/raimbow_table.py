import hashlib
import base64

def generate_hash(password):
    md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
    
    base64_hash = base64.b64encode(md5_hash.encode('utf-8')).decode('utf-8')
    
    sha1_hash = hashlib.sha1(base64_hash.encode('utf-8')).hexdigest()
    
    return sha1_hash

target_hash = "<ADICIONE O HASH AQUI>"

with open('password.lst', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        password = line.strip()
        if not password:
            continue
        
        current_hash = generate_hash(password)
        
        if current_hash == target_hash:
            print(f"Senha encontrada: {password}")
            break
    else:
        print("Senha não encontrada na wordlist.")