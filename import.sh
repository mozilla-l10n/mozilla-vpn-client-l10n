#!bin/bash
/usr/lib/qt5/bin/lupdate vpn/src/src.pro -ts

for filename in vpn/translations/* do 
    /usr/lib/qt5/bin/lconvert -i filename -o translationFiles/${basename filename}.xlf; 
done