#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Verwendung: ./wavtomp.sh datei.wav"
    exit 1
fi

INPUT="$1"
OUTPUT="${INPUT%.wav}.mp3"

ffmpeg -i "$INPUT" -b:a 192k "$OUTPUT"

if [ $? -ne 0 ]
then
    echo "Fehler bei der Umwandlung"
    exit 1
fi

exit 0