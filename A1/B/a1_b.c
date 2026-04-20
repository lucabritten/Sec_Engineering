#include <stdio.h>
#include <time.h>

int main(void) {
	time_t raw_time;
	struct tm *info;
	char buffer[50];

	time(&raw_time);

	info = localtime(&raw_time);

	strftime(buffer, 50,"%a %b  %d %X %Z %Y", info);
	printf("%s\n",buffer);
}

