#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# This script must be executed at the root of the repository.

from lxml import etree, objectify
from translate.misc.xml_helpers import reindent
import os

vpn_project_folder = "vpn"
output_folder = "translationFiles"

srcFile = os.path.join(vpn_project_folder, "src", "src.pro")
os.system(f"lupdate {srcFile} -ts")

filePath = os.path.join(vpn_project_folder, "translations", "mozillavpn_en.ts")
outFile = os.path.join(output_folder, "en", "mozillavpn.xliff")

# Update English XLIFF file
print(f"Updating {outFile}")
os.system(f"lconvert -if ts -i {filePath} -of xlf -o {outFile}")

# Clean up the new XLIFF file
NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
tree = etree.parse(outFile)
root = tree.getroot()
objectify.deannotate(root, cleanup_namespaces=True)

# Remove targets (i.e. translations) if present, since this is the reference
# locale
for target in root.xpath("//x:target", namespaces=NS):
    if target is not None:
        target.getparent().remove(target)

# If defined in the <target>, move the xml:space attribute to the
# parent <trans-unit> element
for source in root.xpath("//x:source", namespaces=NS):
    attrib_name = "{http://www.w3.org/XML/1998/namespace}space"
    xml_space = source.get(attrib_name)
    if xml_space is not None:
        source.getparent().set(attrib_name, xml_space)

# Change QT <extracomment> elements into <notes>
for extracomment in root.xpath("//x:extracomment", namespaces=NS):
    extracomment.tag = "note"

# Remove all <context-group> elements
for context_group in root.xpath("//x:context-group", namespaces=NS):
    context_group.getparent().remove(context_group)

# Replace the existing locale file with the new XML content
with open(outFile, "w") as fp:
    # Fix identation of XML file
    reindent(root)
    xliff_content = etree.tostring(
        tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
    )
    fp.write(xliff_content.decode("utf-8"))
