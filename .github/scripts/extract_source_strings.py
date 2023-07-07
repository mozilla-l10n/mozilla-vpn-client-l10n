#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# This script must be executed at the root of the repository.

from lxml import etree, objectify
from translate.misc.xml_helpers import reindent
import argparse
import os
import re


def get_node_key(node, attr=None):
    if attr in node.attrib:
        return f"{node.tag}:{node.get(attr)}"
    return f"{node.tag}"


def sort_children(node, attr=None):
    node[:] = sorted(node, key=lambda child: get_node_key(child, attr))
    for child in node:
        sort_children(child, attr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        required=True,
        dest="input_path",
        help="Path to the .ts file to import strings from.",
    )
    parser.add_argument(
        "--output",
        required=True,
        dest="output_file",
        help="Path to the output XLIFF file",
    )
    parser.add_argument(
        "--lib",
        required=False,
        default="",
        dest="lib_path",
        help="Path to qt libraries",
    )
    args = parser.parse_args()

    output_xliff_file = args.output_file

    # Update English XLIFF file
    print(f"Extracting strings in {output_xliff_file}")
    exe_path = os.path.join(args.lib_path, "lconvert")
    os.system(f"{exe_path} -if ts -i {args.input_path} -of xlf -o {output_xliff_file}")

    # Clean up the new XLIFF file
    NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
    tree = etree.parse(output_xliff_file)
    root = tree.getroot()
    objectify.deannotate(root, cleanup_namespaces=True)

    # Work around the change of file path caused by exporting translations
    # in subfolders
    # https://github.com/mozilla-mobile/mozilla-vpn-client/pull/1284
    for f in root.xpath("//x:file", namespaces=NS):
        if "original" in f.attrib:
            file_name = f.get("original")
            # Changes caused by https://github.com/mozilla-l10n/mozilla-vpn-client-l10n/pull/268
            file_name = re.sub(r"^src/", "../src/", file_name)
            file_name = re.sub(r"^nebula/", "../../nebula/", file_name)
            # Changes caused by https://github.com/mozilla-mobile/mozilla-vpn-client/pull/7367
            file_name = re.sub(r"^../src/", "../src/apps/vpn/", file_name)
            if "i18nstrings_p.cpp" in file_name:
                file_name = "generated/l18nstrings_p.cpp"
            f.set("original", file_name)

    # Normalize path for strings generated from strings.yaml, removing "../"
    # (more than once if necessary).
    for f in root.xpath("//x:file", namespaces=NS):
        if "original" in f.attrib:
            file_name = f.get("original")
            if "l18nstrings_p.cpp" in file_name:
                while file_name.startswith("../"):
                    file_name = file_name.lstrip("../")
                f.set("original", file_name)

    # Remove targets (i.e. translations) if present, since this is the reference
    # locale
    for target in root.xpath("//x:target", namespaces=NS):
        if target is not None:
            target.getparent().remove(target)

    # Remove the xml:space attribute in the <source>, since it's not used when
    # exporting back to .ts
    for source in root.xpath("//x:source", namespaces=NS):
        attrib_name = "{http://www.w3.org/XML/1998/namespace}space"
        source.attrib.pop(attrib_name)

    # Change QT <extracomment> elements into <notes>
    for extracomment in root.xpath("//x:extracomment", namespaces=NS):
        extracomment.tag = "note"

    # Remove all <context-group> elements
    for context_group in root.xpath("//x:context-group", namespaces=NS):
        context_group.getparent().remove(context_group)

    # Add target language
    for file_node in root.xpath("//x:file", namespaces=NS):
        file_node.set("target-language", "en-US")

    # Sort file elements by "original" attribute
    sort_children(root, "original")
    # Sort trans-unit elements by IDs within each file element
    for f in root.xpath("//x:file", namespaces=NS):
        sort_children(f, "id")

    # Replace the existing local file with the new XML content
    with open(output_xliff_file, "w") as fp:
        # Fix indentation of XML file
        reindent(root)
        xliff_content = etree.tostring(
            tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
        )
        fp.write(xliff_content.decode("utf-8"))


if __name__ == "__main__":
    main()
