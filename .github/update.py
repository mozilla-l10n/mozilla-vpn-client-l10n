#! /usr/bin/env python3
# Note: this wont work on python 2.7
# This script must be executed at the root of the repository.

import xml.etree.ElementTree as ET
import os
import shutil
import html
from xml.sax import saxutils as su

ET.register_namespace('', 'urn:oasis:names:tc:xliff:document:1.2')
ET.register_namespace('qt', 'urn:trolltech:names:ts:document:1.0')

VPN_PROJECT_DIR = 'vpn'
OUT_PROJECT_DIR = 'translationFiles'

#LCONVERT = '/usr/lib/qt5/bin/lconvert'
LCONVERT = 'lconvert'

# Make sure the Target ts files are up to date
# Generate a translations.pri containing all languages in this repo
qtTranslationProject = open(os.path.join(VPN_PROJECT_DIR,"translations","translations.pri"), "w")
qtTranslationProject.write("TRANSLATIONS += \ \n")
for folder in os.listdir(OUT_PROJECT_DIR):
    if not os.path.isdir(os.path.join(OUT_PROJECT_DIR, folder)):
        continue
    if not len(folder.split("-")[0]) == 2:
        continue
    qtTranslationProject.write(f"../translations/mozillavpn_{folder}.ts  \ \n")

qtTranslationProject.write("\n \n ##End")
qtTranslationProject.close()

srcFile = os.path.join(VPN_PROJECT_DIR, 'src', 'src.pro')
os.system(f'lupdate {srcFile} -ts')

for fileName in os.listdir(os.path.join(VPN_PROJECT_DIR, 'translations')):
    print(f'Reading {fileName}')
    if (not fileName.endswith('.ts')):
        continue
    filePath = os.path.join(VPN_PROJECT_DIR, 'translations', fileName)
    # Usual filename: mozillavpn_zh-cn.ts
    locale = fileName.split('_')[1].split('.')[0] # de, zh-cn, etc.
    baseName = fileName.split('_')[0] # mozillavpn
    outPath = os.path.join(OUT_PROJECT_DIR, locale)
    # Create folder for each locale and convert
    # ts file to /{locale}/mozillavpn.xliff
    if not os.path.exists(outPath):
        print(f'Create Folder for {locale}')
        os.mkdir(outPath)

    outFile = os.path.join(outPath, f'{baseName}.xliff')
    if not os.path.exists(outFile):
        # If the file doesn't exist
        print(f'Creating {outFile}')
        os.system(f'{LCONVERT} -i {filePath} -of xlf -o {outFile}')
    else:
        # Keep current translations
        print(f'Updating {outFile}')
        os.system(f'{LCONVERT} -if ts -i {filePath} -if xlf -i {outFile} -of xlf -o {outFile}')

    # Now clean up the new xliff file
    tree = ET.parse(outFile)
    root = tree.getroot()

    # Iterate all targetElements and remove empty ones
    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
        target = element.find('{urn:oasis:names:tc:xliff:document:1.2}target')
        if (not target.text):
            element.remove(target)

#    # Unescape any html in text
#    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}source'):
#        t = element.text
#        element.clear()
#        element.tail = su.unescape(t)
#        #print(f'Unescaped : {element.text}')

    # Iterate all targetElements and remove empty ones
    for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}extracomment'):
        element.tag = 'note'
    tree.write(outFile)
