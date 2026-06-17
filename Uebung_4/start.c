#include <stdio.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <stdlib.h>

// Refactor to swtich case
int main(int argc, char** argv) {

    if (argc < 2) {
        printf("Usage: %s program [args...]\n", argv[0]);
        return 1;
    }

    pid_t child_pid = fork();
    int child_status;

    if (child_pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (child_pid == 0) {
        if (setpriority(PRIO_PROCESS, 0, 19) < 0) {
            perror("setpriority failed");
        }

        execvp(argv[1], argv + 1);

        perror("execvp failed");
        exit(1);
    }
    else {
        printf("Started child process with PID: %d\n", child_pid);

        wait(&child_status);

        if (WIFEXITED(child_status)) {
            printf("Child exited with return code %d\n",
                   WEXITSTATUS(child_status));
        }

        if (WIFSIGNALED(child_status)) {
            int sig = WTERMSIG(child_status);
            printf("Child terminated by signal %d\n", sig);
            psignal(sig, "Signal description");
        }
    }

    return 0;
}