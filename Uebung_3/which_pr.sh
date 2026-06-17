#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Verwendung: ./which.sh programmname"
    exit 1
fi

PROGRAMM="$1"

for DIR in $(echo "$PATH" | sed 's/:/ /g')
do
    if [ -x "$DIR/$PROGRAMM" ]
    then
        echo "$DIR/$PROGRAMM"
        exit 0
    fi
done

echo "Programm nicht gefunden"
exit 1