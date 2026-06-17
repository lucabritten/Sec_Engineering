#!/bin/bash

ulimit -t 5 # Set max time
ulimit -s 64 # Set max stack size
ulimit -f 100 # Set max file size

# gcc -o run_process run_process.c
./run_process file