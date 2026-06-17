#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void handler(int sig) {
    if (sig == SIGXCPU)
        printf("CPU time limit exceeded!\n");
    else if (sig == SIGXFSZ)
        printf("File size limit exceeded!\n");
    else if (sig == SIGSEGV)
        printf("Stack size limit exceeded!\n");
    exit(1);
}

void exceed_cpu() {
    int i = 0;
    while (1) {
        i += 1;
    }
}

void exceed_stack() {
    exceed_stack();
}

void exceed_file() {
    FILE *f = fopen("bigfile.txt", "w");
    if (f == NULL) {
        printf("Error opening file\n");
        exit(1);
    }
    
    while (1) {
        fprintf(f, "AAAAAAAAAA\n");  // 11 Bytes pro Durchlauf
        fflush(f);                   // sofort auf Disk schreiben
    }
}

int main(int argc, char *argv[]) {
    signal(SIGXCPU, handler);
    signal(SIGXFSZ, handler);
    signal(SIGSEGV, handler);
    
    if (argc < 2) {
        printf("Usage: ./limits <cpu|stack|file>\n");
        exit(1);
    }
    
    if (strcmp(argv[1], "cpu") == 0) {
        exceed_cpu();
    } 
    else if (strcmp(argv[1], "stack") == 0) {
        exceed_stack();
    } else if (strcmp(argv[1], "file") == 0) {
        exceed_file();
    } else {
        printf("Invalid argument: %s", argv[1]);
        exit(1);
    }
}