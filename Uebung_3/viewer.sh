#!/bin/bash

if [ $# -eq 0 ]
then
    echo "ERROR: Keine Argumente übergeben."
    exit 1
fi

FILE="$1"
TYPE=$(file "$FILE")

if echo "$TYPE" | grep -q "JPEG"
then
    PROGRAM="timg"

elif echo "$TYPE" | grep -q "PDF"
then
    PROGRAM="xpdf"

elif echo "$TYPE" | grep -q "text"
then
    PROGRAM="less"

elif echo "$TYPE" | grep -q "OpenDocument"
then
    PROGRAM="libreoffice"

else
    echo "Dateityp unbekannt"
    exit 1
fi

$PROGRAM "$FILE"

if [ $? -ne 0 ]
then
    echo "Fehler beim Starten von $PROGRAM"
    exit 1
fi

exit 0