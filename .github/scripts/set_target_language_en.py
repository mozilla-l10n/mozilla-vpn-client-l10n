#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from glob import glob
from lxml import etree
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "en_path",
        help="Path to the folder to check",
    )
    args = parser.parse_args()

    NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}
    for xliff_path in glob(f"{args.en_path}/**/*.xliff", recursive=True):
        tree = etree.parse(xliff_path)
        root = tree.getroot()

        # Set target language to en-US
        for file_node in root.xpath("//x:file", namespaces=NS):
            file_node.set("target-language", "en-US")

        with open(xliff_path, "w") as fp:
            # Fix indentation of XML file
            etree.indent(root)
            xliff_content = etree.tostring(
                tree, encoding="UTF-8", xml_declaration=True, pretty_print=True
            )
            fp.write(xliff_content.decode("utf-8"))


if __name__ == "__main__":
    main()
