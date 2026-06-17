#include <stdio.h>
#include <stdlib.h>
#include <sys/ipc.h>
#include <sys/shm.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <signal.h>
#include <time.h>
#include <sys/sem.h>

#define N_DATA 2000000
#define N_SHARED 2000


#define SEM_WRITE 0
#define SEM_READ 1

// P-Operation auf einer Semaphore:
// Der Prozess wartet, bis die Semaphore > 0 ist,
// danach wird sie um 1 dekrementiert.
void sem_wait_op(int semid, int semnum) {
    struct sembuf op;
    op.sem_num = semnum;
    // -1 bedeutet: Semaphore herunterzählen (wait)
    op.sem_op = -1;
    op.sem_flg = 0;
    semop(semid, &op, 1);
}

// V-Operation auf einer Semaphore:
// Erhöht die Semaphore um 1 und signalisiert,
// dass ein anderer Prozess fortfahren darf.
void sem_signal_op(int semid, int semnum) {
    struct sembuf op;
    op.sem_num = semnum;
    // +1 bedeutet: Semaphore erhöhen (signal)
    op.sem_op = 1;
    op.sem_flg = 0;
    semop(semid, &op, 1);
}

int main() {
    
    // Initialisierung des Shared-Memory-Blocks
    int shmid;

    shmid = shmget(IPC_PRIVATE, // Neues privates IPC-Objekt für Parent-Child-Kommunikation
                   sizeof(int) * N_SHARED, // Größe des Speichersegments
                   IPC_CREAT | 0666); // Erzeugen des Segments, falls es noch nicht existiert, Zugriffrechte

    if(shmid == -1) {
        perror("Error while executing shmget");
        exit(1);
    }

    int *shared;

    // Shared Memory in den virtuellen Adressraum des Prozesses einbinden
    shared = (int *) shmat(shmid, NULL, 0);

    if(shared == (void *) -1) {
        perror("Error while executing shmat");
        exit(1);
    }

    int semid;

    // Erzeugen eines Semaphore-Sets mit zwei Semaphoren:
    // SEM_WRITE -> steuert Schreibzugriff
    // SEM_READ  -> steuert Lesezugriff
    semid = semget(IPC_PRIVATE, 2, IPC_CREAT | 0666);

    if (semid == -1) {
        perror("semget");
        exit(1);
    }
    // Initialzustand:
    // Schreiben erlaubt (1), Lesen blockiert (0)
    semctl(semid, SEM_WRITE, SETVAL, 1);
    semctl(semid, SEM_READ, SETVAL, 0);

    // Erzeugen des Child-Prozesses.
    // Child erhält Kopie der Shared-Memory- und Semaphore-IDs.
    pid_t child_pid = fork();

    if (child_pid < 0) {
        perror("fork failed");
        return 1;
    }
    else if (child_pid == 0) {

        for(int offset = 0; offset < N_DATA; offset += N_SHARED) {
            // Warten bis der Parent Daten geschrieben hat
            sem_wait_op(semid, SEM_READ);

            // Auslesen der Daten aus dem Shared Memory
            for(int i=0; i<N_SHARED;i++) {
                printf("%d\n",shared[i]);
            }

            // Signalisiert dem Parent, dass wieder geschrieben werden darf
            sem_signal_op(semid, SEM_WRITE);
        }

        shmdt(shared);
    }
    else {

        // Initialisierung des Zufallszahlengenerators
        srand48(time(NULL));
        for(int offset = 0; offset < N_DATA; offset += N_SHARED) {
            // Warten bis Schreiben erlaubt ist
            sem_wait_op(semid, SEM_WRITE);

            // Schreiben von Zufallszahlen in den Shared-Memory-Bereich
            for(int i=0; i< N_SHARED;i++){
                shared[i] = lrand48();
            }

            // Signalisiert dem Child, dass Daten gelesen werden können
            sem_signal_op(semid, SEM_READ);
        }
        // Parent wartet auf Beendigung des Child-Prozesses
        wait(NULL);

        // Freigeben und Löschen aller IPC-Ressourcen
        shmdt(shared);
        shmctl(shmid, IPC_RMID, NULL);
        semctl(semid, 0, IPC_RMID);
    }

    return 0;
}