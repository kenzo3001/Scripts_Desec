#!/usr/bin/env python3
"""
Script de fuzzing de buffer: envia cargas de tamanhos crescentes para um serviço de rede
para testar vulnerabilidades de buffer overflow. Permite configurar o alvo e parâmetros via CLI.
"""
import socket
import argparse
import logging
import time
import sys

def generate_payloads(min_length, max_length, step, char='A'):
    """
    Gera uma lista de payloads (strings) para fuzzing.
    Inicia com `min_length` repetições do caractere `char` e vai aumentando
    até `max_length`, incrementando de `step` em `step`.
    """
    payloads = []
    if min_length <= 0 or step <= 0 or max_length <= 0:
        # Não faz sentido gerar payloads se algum parâmetro não for positivo
        return payloads
    length = min_length
    while length <= max_length:
        payloads.append(char * length)
        length += step
    # Se o último payload gerado não atingir exatamente max_length, inclui um payload final de tamanho max_length
    if payloads and len(payloads[-1]) < max_length:
        payloads.append(char * max_length)
    elif not payloads:
        # Se a lista está vazia (por ex. min_length > max_length), retorna um payload de tamanho max_length
        payloads = [char * max_length]
    return payloads

def fuzz_target(ip, port, payloads, prefix="SEND ", suffix="\r\n", timeout=5.0, delay=0.0):
    """
    Envia cada payload da lista `payloads` para o serviço de destino (ip, port).
    O texto `prefix` é enviado antes do payload, e `suffix` após, em cada mensagem.
    `timeout` define o tempo máximo de espera para conexão e operações de recv.
    `delay` define o intervalo (em segundos) entre envios de payloads (para evitar sobrecarregar o alvo).
    """
    for payload in payloads:
        try:
            # Cria o socket TCP IPv4 e estabelece conexão
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                logging.info("Enviando payload de tamanho %d bytes...", len(payload))
                s.connect((ip, port))
                # Tenta receber banner inicial do serviço, se existir
                try:
                    banner = s.recv(1024)
                    if banner:
                        logging.debug("Banner recebido: %s", banner.decode(errors='ignore').strip())
                except socket.timeout:
                    logging.debug("Nenhum banner recebido (timeout atingido).")
                # Monta a mensagem completa (prefixo + payload + sufixo) e envia
                message = f"{prefix}{payload}{suffix}"
                s.sendall(message.encode('utf-8'))  # sendall envia todos os bytes do payload ou lança exceção em caso de erro
                # (Não é necessário receber resposta após o envio para fins de fuzzing)
        except Exception as e:
            # Em caso de erro (ex: conexão recusada ou travamento do serviço alvo)
            logging.error("Erro ao enviar payload de tamanho %d: %s", len(payload), e)
            logging.error("Interrompendo o fuzzing devido ao erro acima.")
            break
        # Aguarda um intervalo definido antes de enviar o próximo payload (se especificado)
        if delay > 0:
            time.sleep(delay)

def main():
    parser = argparse.ArgumentParser(description="Script de fuzzing que envia buffers crescentes a um serviço de rede para testar vulnerabilidade de buffer overflow.")
    parser.add_argument('--ip', dest='ip', type=str, default='127.0.0.1',
                        help='Endereço IP do alvo (default: 127.0.0.1)')
    parser.add_argument('--port', dest='port', type=int, default=9999,
                        help='Porta TCP do serviço alvo (default: 9999)')
    parser.add_argument('--min-length', dest='min_length', type=int, default=1,
                        help='Tamanho inicial do buffer de fuzz (default: 1 byte)')
    parser.add_argument('--max-length', dest='max_length', type=int, default=300,
                        help='Tamanho máximo do buffer de fuzz (default: 300 bytes)')
    parser.add_argument('--step', dest='step', type=int, default=100,
                        help='Aumento do tamanho do buffer a cada etapa (default: 100 bytes)')
    parser.add_argument('--delay', dest='delay', type=float, default=0.0,
                        help='Delay em segundos entre envios de payloads (default: 0.0)')
    parser.add_argument('--timeout', dest='timeout', type=float, default=5.0,
                        help='Timeout em segundos para conexão e operações de rede (default: 5.0)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Ativa modo verboso (detalhado) no log de saída')
    args = parser.parse_args()

    # Configuração do nível de logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    # Validação básica dos parâmetros numéricos
    if args.min_length <= 0 or args.max_length <= 0 or args.step <= 0:
        logging.error("Os parâmetros min-length, max-length e step devem ser inteiros positivos.")
        sys.exit(1)
    if args.min_length > args.max_length:
        logging.error("O valor de --min-length não pode ser maior que --max-length.")
        sys.exit(1)

    # Gera lista de payloads para fuzzing
    payloads = generate_payloads(args.min_length, args.max_length, args.step)
    if not payloads:
        logging.error("Nenhum payload gerado - verifique os parâmetros fornecidos.")
        sys.exit(1)

    logging.info("Iniciando fuzzing em %s:%d com %d payload(s) (min: %d byte(s), max: %d byte(s), incremento: %d)",
                 args.ip, args.port, len(payloads), args.min_length, args.max_length, args.step)
    if args.delay > 0:
        logging.info("Delay de %.2f segundo(s) entre envios.", args.delay)
    # Inicia o processo de fuzzing com os parâmetros fornecidos
    fuzz_target(args.ip, args.port, payloads, prefix="SEND ", suffix="\r\n", timeout=args.timeout, delay=args.delay)

if __name__ == "__main__":
    main()
