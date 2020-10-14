#! /usr/bin/env bash

# Updates QT Translation sources, converts them into XLIFF
# Usage ./import.sh /path/to/mozVPN/ /path/to/translateGit
#
# lupdate & lconvert with qml support must be available

LUPDATE=$(which lupdate)
LCONVERT=$(which lconvert)

LUPDATE vpn/src/src.pro -ts

for FILE in $1/translations/*; do
    OUT_FILE="$2/$(basename '$FILE' .ts).xliff"
    if [ -f $OUT_FILE ]; then
        echo "Updating $OUT_FILE"
        LCONVERT -i "$FILE" -i $OUT_FILE -o $OUT_FILE
    else
        echo "Importing $OUT_FILE"
        LCONVERT -i "$FILE" -o $OUT_FILE
    fi
done
