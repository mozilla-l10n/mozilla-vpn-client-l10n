#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
 update_other_locales.py --reference <locale> --path <base_l10n_folder> --xliff <xliff_filename> [optional list of locales]

  For each folder (locale) available in base_l10n_folder:

  1. Read existing translations, store them in an array: IDs use the structure
     file_name:string_id:source_hash. Using the hash of the source string
     prevents from keeping an existing translation if the ID doesn't change
     but the source string does.

     If the '--nofile' argument is passed, the 'file_name' won't be used when
     storing translations. This allows to retain translations when a string
     moves as-is from one file to another.

  2. Inject available translations in the reference XLIFF file, updating
     the target-language where available on file elements.

  3. Store the updated content in existing locale files, without backup.
"""

from copy import deepcopy
from glob import glob
from lxml import etree
from translate.misc.xml_helpers import reindent
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
    parser.add_argument(
        "--xliff",
        required=True,
        dest="xliff_filename",
        help="Name of the XLIFF file to process",
    )
    parser.add_argument(
        "--nofile",
        required=False,
        dest="ignore_file",
        action="store_true",
        help="Ignore the 'file' element when storing existing translations, only use IDs and source string",
    )
    parser.add_argument("locales", nargs="*", help="Locales to process")
    args = parser.parse_args()

    reference_locale = args.reference_locale
    excluded_locales = [reference_locale]

    # Get a list of files to update (absolute paths)
    base_folder = os.path.realpath(args.base_folder)

    reference_file_path = os.path.join(
        base_folder, reference_locale, args.xliff_filename
    )
    if not os.path.isfile(reference_file_path):
        sys.exit(f"Requested reference file doesn't exist: {reference_file_path}")

    file_paths = []
    if not args.locales:
        for xliff_path in glob(base_folder + "/*/" + args.xliff_filename):
            parts = xliff_path.split(os.sep)
            if not parts[-2] in excluded_locales:
                file_paths.append(xliff_path)
    else:
        for locale in args.locales:
            if locale in excluded_locales:
                print(f"Requested locale is in the list of excluded locales: {locale}")
                continue

            if os.path.isdir(locale):
                file_paths.append(
                    os.path.join(base_folder, locale, args.xliff_filename)
                )
            else:
                print(f"Requested locale doesn't exist: {locale}")

    if not file_paths:
        sys.exit("No locales updated.")
    else:
        file_paths.sort()

    # Read reference XML file
    try:
        reference_tree = etree.parse(reference_file_path)
    except Exception as e:
        sys.exit(f"ERROR: Can't parse reference {reference_locale} file\n{e}")

    for file_path in file_paths:
        print(f"Updating {file_path}")

        # Make a copy of the reference tree and root
        reference_tree_copy = deepcopy(reference_tree)
        reference_root_copy = reference_tree_copy.getroot()

        # Read localized XML file
        try:
            locale_tree = etree.parse(file_path)
            locale_root = locale_tree.getroot()
        except Exception as e:
            print(f"ERROR: Can't parse {file_path}")
            print(e)
            continue

        """
        Using locale folder as locale code for the target-language attribute.
        This can be use to map a locale code to a different one.
        Structure: "locale folder" -> "locale code"
        """
        locale_code = file_path.split(os.sep)[-2]
        locale_mapping = {
            "sv_SE": "sv",  # See bug 1713058
        }
        locale_code = locale_mapping.get(locale_code, locale_code)

        """
         Store existing localizations in a dictionary.
         The key for each translation is a combination of the <file> "original"
         attribute, the <trans-unit> "id", and the <source> text.
         This allows to invalidate a translation if the source string
         changed without using a new ID.
        """
        translations = {}
        for trans_node in locale_root.xpath("//x:trans-unit", namespaces=NS):
            for child in trans_node.xpath("./x:target", namespaces=NS):
                file_name = trans_node.getparent().getparent().get("original")
                source_string = trans_node.xpath("./x:source", namespaces=NS)[0].text
                if args.ignore_file:
                    string_id = f"{trans_node.get('id')}:{hash(source_string)}"
                else:
                    string_id = (
                        f"{file_name}:{trans_node.get('id')}:{hash(source_string)}"
                    )
                translations[string_id] = child.text

        # Inject available translations in the reference XML
        for trans_node in reference_root_copy.xpath("//x:trans-unit", namespaces=NS):
            # Add xml:space="preserve" to all trans-units, to avoid conflict
            # with Pontoon
            attrib_name = "{http://www.w3.org/XML/1998/namespace}space"
            xml_space = trans_node.get(attrib_name)
            if xml_space is None:
                trans_node.set(attrib_name, "preserve")

            file_name = trans_node.getparent().getparent().get("original")
            source_string = trans_node.xpath("./x:source", namespaces=NS)[0].text
            original_id = trans_node.get("id")
            if args.ignore_file:
                string_id = f"{original_id}:{hash(source_string)}"
            else:
                string_id = f"{file_name}:{original_id}:{hash(source_string)}"
            updated = False
            translated = string_id in translations
            for child in trans_node.xpath("./x:target", namespaces=NS):
                if translated:
                    child.text = translations[string_id]
                else:
                    # No translation available, remove the target
                    child.getparent().remove(child)
                updated = True

            if translated and not updated:
                # Translation is available, but the refence XLIFF has no target.
                # Create a target node and insert it after source.
                child = etree.Element("target")
                child.text = translations[string_id]
                trans_node.insert(1, child)

        # Update target-language where defined, replace underscores with
        # hyphens if necessary (e.g. en_GB => en-GB).
        for file_node in reference_root_copy.xpath("//x:file", namespaces=NS):
            if file_node.get("target-language"):
                file_node.set("target-language", locale_code.replace("_", "-"))

        # Replace the existing locale file with the new XML content
        with open(file_path, "w") as fp:
            # Fix identation of XML file
            reindent(reference_root_copy)
            xliff_content = etree.tostring(
                reference_tree_copy,
                encoding="UTF-8",
                xml_declaration=True,
                pretty_print=True,
            )
            fp.write(xliff_content.decode("utf-8"))


if __name__ == "__main__":
    main()
