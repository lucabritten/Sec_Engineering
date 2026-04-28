#include <stdio.h>
#include <time.h>

int main(void) {
	time_t seconds;
	struct tm *info;
	char buffer[50];

	time(&seconds);

	info = localtime(&seconds);

	strftime(buffer, 50,"%a %b  %d %X %Z %Y", info);
	printf("%s\n",buffer);
}