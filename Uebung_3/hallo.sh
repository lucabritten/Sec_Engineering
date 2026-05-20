#!/bin/bash

if [ $# -eq 0 ]
then
    echo "ERROR: No args available"
    exit 1
fi

for name in "$@"
do
    echo "Hallo $name"
done

exit 0