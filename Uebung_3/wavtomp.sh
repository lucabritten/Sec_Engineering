#!/bin/sh

if [ $# -ne 1 ]
then
    echo "Verwendung: ./wavtomp.sh datei.wav"
    exit 1
fi

case "$1" in
    *.wav)
        ;;
    *)
        echo "ERROR: Datei muss auf .wav enden"
        exit 1
        ;;
esac


INPUT="$1"
OUTPUT="${INPUT%.wav}.mp3"

ffmpeg -i "$INPUT" -b:a 192k "$OUTPUT"

if [ $? -ne 0 ]
then
    echo "Fehler bei der Umwandlung"
    exit 1
fi

exit 0