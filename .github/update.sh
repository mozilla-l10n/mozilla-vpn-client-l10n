#! /usr/bin/env bash

# Updates QT Translation sources, converts them into xlf
# Usage ./import.sh /path/to/mozVPN/ /path/to/translateGit
#
# lupdate & lconvert with qml support must be available

LUPDATE=$(which lupdate)
LCONVERT=$(which lconvert)

LUPDATE vpn/src/src.pro -ts

for FILE in $1/translations/*; do
if [ -f "$2/$(basename '$FILE' .ts).xliff" ]; then
    echo "Updating $2/$(basename '$FILE' .ts).xliff"
    LCONVERT -i "$FILE" -i $2/"$(basename "$FILE" .ts)".xliff -o $2/"$(basename "$FILE" .ts)".xliff
else
    echo "Importing $2/$(basename '$FILE' .ts).xliff"
    LCONVERT -i "$FILE" -o $2/"$(basename "$FILE" .ts)".xliff
fi

done
