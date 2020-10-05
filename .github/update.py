#!/usr/bin/python3
# Note: this wont work on python 2.7
# This script must be executed at the root of the repository.

import xml.etree.ElementTree as ET
import os
import shutil
import html
from xml.sax import saxutils as su

ET.register_namespace('', "urn:oasis:names:tc:xliff:document:1.2")
ET.register_namespace('qt', "urn:trolltech:names:ts:document:1.0")

VPN_PROJECT_DIR ="vpn/" 
OUT_PROJECT_DIR ="translationFiles/"

#LCONVERT = "/usr/lib/qt5/bin/lconvert"

LCONVERT = "lconvert"

# Make sure the Target ts files are up to date
os.system(f'lupdate {VPN_PROJECT_DIR}src/src.pro -ts')

for fileName in os.listdir(f'{VPN_PROJECT_DIR}/translations/'):
    if(not fileName.endswith(".ts")):
        continue
    filePath = f'{VPN_PROJECT_DIR}/translations/{fileName}'
    # Usual filename -> mozillavpn_zh-cn.ts
    language = fileName.split("_")[1].split(".")[0] # de , zh-cn ...
    basename = fileName.split("_")[0] # mozillavpn
    outPath = f'{OUT_PROJECT_DIR}/{language}'
    # Create folder for each language and convert 
    # ts file to /{lang}/mozillavpn.xlf
    print(f"Checking {language}")
    if not os.path.exists(outPath):
        os.mkdir(outPath)
    
    if not os.path.exists(f'{outPath}/{basename}.xlf'):
        # If the not file exsists
        print(f"Creating {outPath}/{basename}")
        os.system(f'{LCONVERT} -i {filePath} -o {outPath}/{basename}.xlf')
    else:
        # keep its current translations
        print(f"Updating {outPath}/{basename}")
        os.system(f'{LCONVERT} -i {filePath} -i {outPath}/{basename}.xlf -o {outPath}/{basename}.xlf')

    outFile = f'{outPath}/{basename}.xlf'
    ## Now Clean the new xlf a bit up
    tree = ET.parse(f'{outPath}/{basename}.xlf')
    root = tree.getroot()

    #Iterate all targetElements and remove empty ones
    for element in root.iter("{urn:oasis:names:tc:xliff:document:1.2}trans-unit"):
        target = element.find("{urn:oasis:names:tc:xliff:document:1.2}target")
        if(not target.text):
            element.remove(target)

#    #Unescape any html in text
#    for element in root.iter("{urn:oasis:names:tc:xliff:document:1.2}source"):
#        t = element.text
#        element.clear()
#        element.tail = su.unescape(t)
#        #print(f'Unescaped : {element.text}')

    #Iterate all targetElements and remove empty ones
    for element in root.iter("{urn:oasis:names:tc:xliff:document:1.2}extracomment"):
        element.tag="note"
    tree.write(f'{outPath}/{basename}.xlf')

