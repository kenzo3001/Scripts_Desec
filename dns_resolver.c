#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>

#define TAM_MAX 256

void mostrar_demo() {
    printf("==========================================\n");
    printf("           🔍 DNS RESOLVER 🔍            \n");
    printf("==========================================\n");
    printf("➡️  O script tenta resolver subdomínios de um alvo usando uma lista de prefixos.\n");
    printf("➡️  Ele concatena cada subdomínio ao domínio principal e busca o IP correspondente.\n");
    printf("➡️  Exemplo de uso: ./dns_resolver alvo.com.br lista.txt\n");
    printf("------------------------------------------\n\n");
    sleep(3);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        printf("❌ Uso incorreto!\n");
        printf("Modo correto: %s <domínio> <arquivo_lista>\n", argv[0]);
        return 1;
    }

    mostrar_demo();

    char *alvo = argv[1];
    FILE *arquivo = fopen(argv[2], "r");
    
    if (!arquivo) {
        perror("Erro ao abrir o arquivo");
        return 1;
    }

    char subdominio[TAM_MAX];
    while (fscanf(arquivo, "%255s", subdominio) == 1) {
        char resultado[TAM_MAX];
        int tamanho = snprintf(resultado, TAM_MAX, "%s.%s", subdominio, alvo);

        if (tamanho < 0 || tamanho >= TAM_MAX) {
            fprintf(stderr, "⚠️  Subdomínio muito grande: %s\n", subdominio);
            continue;
        }

        struct addrinfo hints, *res = NULL;
        memset(&hints, 0, sizeof(hints));
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;

        int status = getaddrinfo(resultado, NULL, &hints, &res);
        if (status != 0) {
            int ignorable = (status == EAI_NONAME);
#ifdef EAI_NODATA
            ignorable = ignorable || (status == EAI_NODATA);
#endif

            if (!ignorable) {
                fprintf(stderr, "⚠️  Falha ao resolver %s: %s\n", resultado, gai_strerror(status));
            }
            if (res) {
                freeaddrinfo(res);
            }
            continue;
        }

        for (struct addrinfo *ptr = res; ptr != NULL; ptr = ptr->ai_next) {
            if (ptr->ai_family != AF_INET) {
                continue;
            }

            struct sockaddr_in *addr = (struct sockaddr_in *)ptr->ai_addr;
            printf("🔹 HOST ENCONTRADO: %s ==> IP: %s\n", resultado, inet_ntoa(addr->sin_addr));
        }

        freeaddrinfo(res);
    }

    fclose(arquivo);
    printf("\n✅ Varredura concluída!\n");
    return 0;
}
