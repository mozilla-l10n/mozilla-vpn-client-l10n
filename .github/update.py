#! /usr/bin/env python3
# Note: this wont work on python 2.7
# This script must be executed at the root of the repository.

import xml.etree.ElementTree as ET
import os

ET.register_namespace('', 'urn:oasis:names:tc:xliff:document:1.2')
ET.register_namespace('qt', 'urn:trolltech:names:ts:document:1.0')

VPN_PROJECT_DIR = 'vpn'
OUT_PROJECT_DIR = 'translationFiles'

srcFile = os.path.join(VPN_PROJECT_DIR, 'src', 'src.pro')
os.system(f'lupdate {srcFile} -ts')

filePath = os.path.join(VPN_PROJECT_DIR, 'translations', 'mozillavpn_en.ts')
outFile = os.path.join(OUT_PROJECT_DIR, 'en', 'mozillavpn.xliff')

# Keep current translations
print(f'Updating {outFile}')
os.system(f'lconvert -if ts -i {filePath} -of xlf -o {outFile}')

# Now clean up the new xliff file
tree = ET.parse(outFile)
root = tree.getroot()

# Iterate all targetElements and remove empty ones
for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}trans-unit'):
    target = element.find('{urn:oasis:names:tc:xliff:document:1.2}target')
    if (not target.text):
        element.remove(target)

# Iterate all targetElements and remove empty ones
for element in root.iter('{urn:oasis:names:tc:xliff:document:1.2}extracomment'):
    element.tag = 'note'
tree.write(outFile)
