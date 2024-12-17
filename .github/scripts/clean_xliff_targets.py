#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# This script must be executed at the root of the repository.

from functions import write_xliff
from lxml import etree, objectify
import argparse


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
        "xliff_file",
        help="Path to the input XLIFF file",
    )
    args = parser.parse_args()
    xliff_file = args.xliff_file

    # Clean up the new XLIFF file
    NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
    tree = etree.parse(xliff_file)
    root = tree.getroot()
    objectify.deannotate(root, cleanup_namespaces=True)

    # Remove targets (i.e. translations) if present, since this is the reference
    # locale
    for target in root.xpath("//x:target", namespaces=NS):
        if target is not None:
            target.getparent().remove(target)

    # Sort file elements by "original" attribute
    sort_children(root, "original")
    # Sort trans-unit elements by IDs within each file element
    for f in root.xpath("//x:file", namespaces=NS):
        sort_children(f, "id")

    # Replace the existing local file with the new XML content
    write_xliff(root, xliff_file)


if __name__ == "__main__":
    main()
