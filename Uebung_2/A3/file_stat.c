#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdio.h>
#include <time.h>
#include <pwd.h>

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Please provide at least one filepath!");
        return 1;
    }

    for (int i = 1; i < argc; i++) {
        struct stat file;

        if (lstat(argv[i], &file) == -1) {
            perror("lstat failed");
            continue;
        }

        printf("[File no. %d]: %s\n", i, argv[i]);

        printf("\tFiletype: ");
        if (S_ISREG(file.st_mode)) printf("regular file\n");
        else if (S_ISDIR(file.st_mode)) printf("directory\n");
        else if (S_ISFIFO(file.st_mode)) printf("pipe\n");
        else if (S_ISSOCK(file.st_mode)) printf("socket\n");
        else if (S_ISCHR(file.st_mode)) printf("char device\n");
        else if (S_ISLNK(file.st_mode)) printf("symbolic link\n");
        else printf("unknown\n");

        printf("\tUID: %d\n", file.st_uid);

        struct passwd *p = getpwuid(file.st_uid);
        if (p)
            printf("\tCorresponding user: %s\n", p->pw_name);
        else
            printf("\tCorresponding user: unknown\n");

        printf("\tGID: %d\n", file.st_gid);
        printf("\tZugriffsbits: %o\n", file.st_mode & 0777);

        printf("\tLast access: %s\n", ctime(&file.st_atime));
        printf("\tLast inode change: %s\n", ctime(&file.st_ctime));
        printf("\tLast file change: %s\n", ctime(&file.st_mtime));
        printf("\tFile creation: %s\n", ctime(&file.st_birthtime));
    }
    return 0;
}
