#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <pwd.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Please provide at least one filepath!");
        return 1;
    }

    printf("You entered %d arguments\n", argc);
    struct stat file_arr[argc];

    for (int i = 1;i < argc; i++) { 
        printf("[File no. %d]: %s\n", i, argv[i]);

        lstat(argv[i], &file_arr[i]);
        struct passwd *p;
        p = getpwuid(file_arr[i].st_uid);


        printf("\tFiletype: %hu\n", file_arr[i].st_mode);
        printf("\tUID: %d", file_arr[i].st_uid);
        printf("Corresponding user: %s\n", p->pw_name);
    }
    return 0;
}