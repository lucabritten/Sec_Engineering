#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Verwendung: ./which.sh programmname"
    exit 1
fi

PROGRAMM="$1"

OLD_IFS="$IFS"
IFS=":"

for DIR in $PATH
do
    if [ -x "$DIR/$PROGRAMM" ]
    then
        echo "$DIR/$PROGRAMM"
        IFS="$OLD_IFS"
        exit 0
    fi
 done

IFS="$OLD_IFS"

echo "Programm nicht gefunden"
exit 1