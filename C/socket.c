#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>

int main(void) {
    int meuSocket;
    int conecta;

    struct sockaddr_in alvo;

    meuSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (meuSocket < 0) {
        perror("Erro ao criar socket");
        return 1;
    }

    alvo.sin_family = AF_INET;
    alvo.sin_port = htons(80);
    alvo.sin_addr.s_addr = inet_addr("192.168.0.1"); 

    conecta = connect(meuSocket, (struct sockaddr *)&alvo, sizeof(alvo));
    if (conecta == 0) {
        printf("✅ Porta 80 aberta!\n");
        close(meuSocket);
    } else {
        printf("❌ Porta 80 fechada ou host inacessível.\n");
    }

    return 0;
}
