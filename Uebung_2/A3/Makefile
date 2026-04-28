CC = gcc
CFLAGS = -Wall -Wextra -std=c11

TARGET = file_stat

all: $(TARGET)

$(TARGET): file_stat.c
	$(CC) $(CFLAGS) file_stat.c -o $(TARGET)

clean:
	rm -f $(TARGET)