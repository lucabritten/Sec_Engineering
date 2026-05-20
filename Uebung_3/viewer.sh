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
    xv "$FILE"

elif echo "$TYPE" | grep -q "PDF"
then
    xpdf "$FILE"

elif echo "$TYPE" | grep -q "text"
then
    less "$FILE"

elif echo "$TYPE" | grep -q "OpenDocument"
then
    libreoffice "$FILE"

else
    echo "Dateityp unbekannt"
    exit 1
fi

exit 0