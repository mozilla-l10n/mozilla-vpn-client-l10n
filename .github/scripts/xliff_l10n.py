#! /usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from collections import defaultdict
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
        "--l10n",
        required=True,
        dest="locales_path",
        help="Path to folder including subfolders for all locales",
    )
    parser.add_argument(
        "--xliff",
        required=True,
        dest="xliff_filename",
        help="Name of the XLIFF file to process",
    )
    parser.add_argument(
        "--dest",
        dest="dest_file",
        help="Save output to file",
    )
    parser.add_argument(
        "--exceptions",
        nargs="?",
        dest="exceptions_file",
        help="Path to JSON exceptions file",
    )
    args = parser.parse_args()

    # Get a list of files to check (absolute paths)
    locales_path = os.path.realpath(args.locales_path)

    file_paths = []
    for xliff_path in glob(locales_path + "/*/" + args.xliff_filename):
        parts = xliff_path.split(os.sep)
        file_paths.append(xliff_path)

    if not file_paths:
        sys.exit("File not found.")
    else:
        file_paths.sort()

    # Load exceptions
    if not args.exceptions_file:
        exceptions = defaultdict(dict)
    else:
        exceptions_filename = os.path.basename(args.exceptions_file)
        try:
            with open(args.exceptions_file) as f:
                exceptions = json.load(f)
        except Exception as e:
            sys.exit(e)

    placeables_pattern = re.compile("(%[1-9ds]?\$?@?)")
    errors = defaultdict(list)
    for file_path in file_paths:
        locale_errors = {}
        # Extract and normalize locale code
        locale = file_path.split(os.sep)[-2].replace("_", "-")

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
                    ) or string_id in tmp_exceptions.get("locales", {}).get(locale, []):
                        continue
                    errors[locale].append(
                        f"'…' missing in {string_id}\n  Translation: {l10n_string}"
                    )

                # Check placeables
                ref_matches = placeables_pattern.findall(ref_string)
                if ref_matches:
                    if string_id in exceptions.get("placeables", {}).get(locale, []):
                        continue
                    ref_matches.sort()
                    l10n_matches = placeables_pattern.findall(l10n_string)
                    l10n_matches.sort()

                    if ref_matches != l10n_matches:
                        errors[locale].append(
                            f"Variable mismatch in {string_id}\n"
                            f"  Translation: {l10n_string}\n"
                            f"  Reference: {ref_string}"
                        )

                # Check pilcrow
                if "¶" in l10n_string:
                    errors[locale].append(
                        f"'¶' in {string_id}\n  Translation: {l10n_string}"
                    )

    if errors:
        locales = list(errors.keys())
        locales.sort()

        output = []
        total_errors = 0
        for locale in locales:
            output.append(f"\nLocale: {locale} ({len(errors[locale])})")
            total_errors += len(errors[locale])
            for e in errors[locale]:
                output.append(f"\n  {e}")
        output.append(f"\nTotal errors: {total_errors}")

        out_file = args.dest_file
        if out_file:
            print(f"Saving output to {out_file}")
            with open(out_file, "w") as f:
                f.write("\n".join(output))
        # Print errors anyway on screen
        print("\n".join(output))
        sys.exit(1)
    else:
        print("No issues found.")


if __name__ == "__main__":
    main()
