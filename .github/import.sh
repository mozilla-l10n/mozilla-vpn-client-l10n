#!/usr/bin/bash
/usr/lib/qt5/bin/lupdate vpn/src/src.pro -ts

for FILE in vpn/translations/*; do 

/usr/lib/qt5/bin/lconvert -i "$FILE" -o translationFiles/"$(basename "$FILE")".xlf

done