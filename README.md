# Mozilla VPN localization

![Linter status](https://github.com/mozilla-l10n/mozl10n-linter/actions/workflows/vpn.yaml/badge.svg)

Localization for the [Mozilla VPN Client](https://github.com/mozilla-mobile/mozilla-vpn-client).

## String updates

Automation is used to extract strings from the code repository, and expose them to all other locales.

1. Strings are extracted and saved in the `en-US` XLIFF file.
2. The updated `en-US` XLIFF is used as a template. Existing translations are copied over if all these elements match:
    * `id` attribute of `trans-unit`.
    * `original` attribute of `file`.
    * `source` text.

As a consequence, the default update removes translations if:
* The source text was changed.
* The string is moved from one file to another.

This is not ideal when the change in the source text is trivial, or the string move is caused by code refactoring.

It’s possible to invoke [automation manually](https://github.com/mozilla-l10n/mozilla-vpn-client-l10n/actions/workflows/update.yaml), and use a different matching criterion:
* `nofile` will copy translations if the ID and source text match, ignoring the file. This is useful to minimize the impact of code refactoring.
* `matchid` will ignore both file and source text, copying translations if the ID matches. This is useful for source changes that don’t require invalidating existing translations.

It’s also possible to provide a `branch` parameter, to use a non-default branch of `mozilla-vpn-client` as starting point. This is useful, for example, to check the impact of large code refactoring from a pull request. Note that the `releases` branch will be used in any case to extract strings.

## License

Translations in this repository are available under the terms of the [Mozilla Public License v2.0](http://www.mozilla.org/MPL/2.0/).
