#include <stdio.h>
#include <time.h>

int main(void) {
    time_t seconds;
    
    time(&seconds);
    
    char *time_string = ctime(&seconds);
    
    printf("%s", time_string);
    
    return 0;
}
