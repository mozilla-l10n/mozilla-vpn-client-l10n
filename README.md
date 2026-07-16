# Mozilla VPN localization

![Linter status](https://github.com/mozilla-l10n/mozl10n-linter/actions/workflows/vpn.yaml/badge.svg)

Localization for the [Mozilla VPN Client](https://github.com/mozilla-mobile/mozilla-vpn-client).

## String updates

Automation is used to extract strings from the code repository, and expose them to all other locales.

1. Strings are extracted and saved in the `en` XLIFF files (the source locale).
2. Pontoon reads `en` as the source locale and keeps every other locale structurally in sync with it, i.e. it adds and removes `trans-unit` elements and files as needed.
3. The default (`standard`) update never changes the structure of localized files: it only removes a translation when the `source` text of that string changed in the reference, and leaves the structure to Pontoon. It does **not** touch a translation when the string is removed from the reference, or moved to a different file — those cases are left to Pontoon (removal) or to a manual run (relocation).

As a consequence, the default update removes translations only when the source text was changed. This is not ideal when the change in the source text is trivial. Moving a string between files does not remove its translation, but it also does not follow the string to its new location: a manual run is needed to relocate it.

It’s possible to invoke [automation manually](https://github.com/mozilla-l10n/mozilla-vpn-client-l10n/actions/workflows/update.yaml), and use a different matching criterion. Unlike `standard`, these modes rebuild each localized file from the `en` structure and re-inject the existing translations, so a translation follows its string to a new `file` instead of being lost when Pontoon later syncs the structure. Translations for strings removed upstream are carried over (their removal is left to Pontoon), not dropped.
* `nofile` keeps translations if the ID and source text match, ignoring the file. This is useful to minimize the impact of code refactoring, e.g. when a string moves between files.
* `matchid` ignores both file and source text, keeping translations if the ID matches (and realigning the source text to the reference). This is useful for source changes that don’t require invalidating existing translations.

It’s also possible to provide a `branch` parameter, to use a non-default branch of `mozilla-vpn-client` as starting point. This is useful, for example, to check the impact of large code refactoring from a pull request. Note that the `releases` branch will be used in any case to extract strings.

## Target language check

Pontoon owns the `target-language` attribute of each `<file>` element. A dedicated [workflow](https://github.com/mozilla-l10n/mozilla-vpn-client-l10n/actions/workflows/check_target_language.yml) runs on pull requests touching XLIFF files, and verifies that every localized file declares the language code expected for its folder. It acts as a safety net that fails if a sync leaves a locale with a wrong or missing code.

## License

Translations in this repository are available under the terms of the [Mozilla Public License v2.0](http://www.mozilla.org/MPL/2.0/).
