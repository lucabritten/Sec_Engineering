#!/bin/bash

if [ $# -eq 0 ]
then
    echo "ERROR: Keine Übergebenen Argumente. Verwendung ./hallo.sh Alice Bob"
    exit 1
fi

for name in "$@"
do
    echo "Hallo $name"
done

exit 0