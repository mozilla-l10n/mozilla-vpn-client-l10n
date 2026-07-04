#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Single source of truth for locale-code mapping between Pontoon folder names
and the codes used in XLIFF target-language attributes.

Mozilla VPN does not remap any locale (folder name == locale code, modulo the
underscore-to-hyphen normalization done by consumers), so the mapping is empty.
Add "folder": "code" entries here if that ever changes.
"""

# Folder code -> target-language code
PONTOON_TO_VPN = {}

# Inverse mapping, generated automatically.
VPN_TO_PONTOON = {v: k for k, v in PONTOON_TO_VPN.items()}
