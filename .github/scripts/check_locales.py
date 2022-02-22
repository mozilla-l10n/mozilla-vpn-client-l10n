#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
 check_locales.py --path <base_l10n_folder> --xliff <xliff_filename>
"""

from glob import glob
from lxml import etree
import argparse
import json
import os
import re
import sys


NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        required=True,
        dest="base_folder",
        help="Path to folder including subfolders for all locales",
    )
    parser.add_argument(
        "--xliff",
        required=True,
        dest="xliff_filename",
        help="Name of the XLIFF file to process",
    )
    args = parser.parse_args()

    # Get a list of files to check (absolute paths)
    base_folder = os.path.realpath(args.base_folder)

    file_paths = []
    for xliff_path in glob(base_folder + "/*/" + args.xliff_filename):
        parts = xliff_path.split(os.sep)
        file_paths.append(xliff_path)

    if not file_paths:
        sys.exit("File not found.")
    else:
        file_paths.sort()

    # Get path to check_exceptions.json from script path
    exception_file = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "check_exceptions.json")
    )
    if os.path.isfile(exception_file):
        with open(exception_file) as f:
            exceptions = json.load(f)
    else:
        print(f"{exception_file} is missing")
        exceptions = {}

    var_pattern = re.compile("(%[1-9])")
    errors = []
    for file_path in file_paths:
        locale_errors = {}
        locale = file_path.split(os.sep)[-2]

        # Read localized XML file
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
        except Exception as e:
            print(f"ERROR: Can't parse {file_path}")
            print(e)
            continue

        for trans_node in root.xpath("//x:trans-unit", namespaces=NS):
            for child in trans_node.xpath("./x:target", namespaces=NS):
                file_name = trans_node.getparent().getparent().get("original")
                string_id = trans_node.get("id")

                ref_string = trans_node.xpath("./x:source", namespaces=NS)[0].text
                l10n_string = child.text

                # Check ellipsis
                if "…" in ref_string and "…" not in l10n_string:
                    tmp_exceptions = exceptions.get("ellipsis", {})
                    if locale in tmp_exceptions.get(
                        "excluded_locales", []
                    ) or string_id in tmp_exceptions.get(locale, []):
                        continue
                    errors.append(
                        f"{locale}: '…' missing in {string_id}\nText: {l10n_string}"
                    )

                # Check variables
                ref_matches = var_pattern.findall(ref_string)
                if ref_matches:
                    if string_id in exceptions.get("variables", {}).get(locale, []):
                        continue
                    ref_matches.sort()
                    l10n_matches = var_pattern.findall(l10n_string)
                    l10n_matches.sort()

                    if ref_matches != l10n_matches:
                        errors.append(
                            f"{locale}: variable mismatch in {string_id}\nText: {l10n_string}"
                        )

                # Check pilcrow
                if "¶" in l10n_string:
                    errors.append(f"{locale}: '¶' in {string_id}\nText: {l10n_string}")

    if errors:
        print("ERRORS:")
        print("\n".join(errors))
        sys.exit(1)
    else:
        print("No errors found.")


if __name__ == "__main__":
    main()
