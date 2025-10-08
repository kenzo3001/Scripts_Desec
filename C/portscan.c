#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>         
#include <sys/socket.h>      
#include <arpa/inet.h>      
#include <netinet/in.h>     

int main(int argc, char *argv[]) {

    int meuSocket;
    int conecta;
    int porta;
    int inicio = 1;
    int final = 65535;
    char *destino;

    if (argc != 2) {
        printf("Modo de uso: %s <IP>\n", argv[0]);
        exit(1);
    }

    destino = argv[1];
    struct sockaddr_in alvo;

    printf("🔎 Iniciando scan em %s...\n\n", destino);

    alvo.sin_family = AF_INET;
    alvo.sin_addr.s_addr = inet_addr(destino);

    for (porta = inicio; porta <= final; porta++) {
        meuSocket = socket(AF_INET, SOCK_STREAM, 0);
        if (meuSocket < 0) {
            perror("Erro ao criar socket");
            exit(1);
        }

        alvo.sin_port = htons(porta);

        conecta = connect(meuSocket, (struct sockaddr *)&alvo, sizeof(alvo));

        if (conecta == 0) {
            printf("🟢 Porta %d - {ABERTA}\n", porta);
        }

        close(meuSocket);
    }

    printf("\n✅ Scan finalizado.\n");

    return 0;
}
