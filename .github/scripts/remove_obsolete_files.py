#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
remove_obsolete_files.py --reference <locale> --path <base_l10n_folder>

 Get a list of all XLIFF files in the reference locale. Then remove all
 extra XLIFF files in locale folders.
"""

from glob import glob
import argparse
import os
import sys


NS = {"x": "urn:oasis:names:tc:xliff:document:1.2"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference",
        required=True,
        dest="reference_locale",
        help="Reference locale code",
    )
    parser.add_argument(
        "--path",
        required=True,
        dest="base_folder",
        help="Path to folder including subfolders for all locales",
    )
    parser.add_argument("locales", nargs="*", help="Locales to process")
    args = parser.parse_args()

    reference_locale = args.reference_locale

    # Get a list of files to update (absolute paths)
    base_folder = os.path.realpath(args.base_folder)
    reference_path = os.path.join(base_folder, reference_locale)

    # Get a list of all the reference XLIFF files
    reference_files = []
    for xliff_path in glob(f"{reference_path}/**/*.xliff", recursive=True):
        reference_files.append(os.path.relpath(xliff_path, reference_path))
    if not reference_files:
        sys.exit(
            f"No reference file found in {os.path.join(base_folder, reference_locale)}"
        )

    # Get the list of locales
    locales = [
        d
        for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d)) and not d.startswith(".")
    ]
    locales.remove(reference_locale)
    locales.sort()

    # Get the list of obsolete XLIFF files
    extra_files = []
    for locale in locales:
        # Get the list of XLIFF files in locale
        locale_files = []
        locale_path = os.path.join(base_folder, locale)
        for xliff_path in glob(f"{locale_path}/**/*.xliff", recursive=True):
            locale_files.append(os.path.relpath(xliff_path, locale_path))

        extra_files_locale = [
            f"{locale}/{filename}"
            for filename in locale_files
            if filename not in reference_files
        ]
        extra_files += extra_files_locale

    # Remove files
    for f in extra_files:
        print(f"Removing {f}")
        os.remove(os.path.join(base_folder, f))


if __name__ == "__main__":
    main()
