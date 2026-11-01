# postalcheck guide

Use postalcheck for offline format checks and consistent form input. It does not query
postal operators, check assignment, or validate street addresses. The snapshot contains
legacy formats as well as current ones. Examples are source examples, not guarantees.

## Public API

Import only from `postalcheck`. The stable names are `is_valid(country, code) -> bool`,
`normalize(country, code) -> str`, `example(country) -> str`,
`supported_countries() -> tuple[str, ...]`, `UnknownCountryError(country,
has_postal_codes=None)` and `InvalidPostalCodeError(country, code)`. All parameters
accept positional or keyword arguments. `__version__` is the release string.

```python
from postalcheck import is_valid, normalize, example, supported_countries

assert is_valid("US", "95014")
assert normalize("uk", "sw1a1aa") == "SW1A 1AA"
assert example("JP") == "154-0023"
assert "GB" in supported_countries() and "UK" not in supported_countries()
```

Country strings are stripped of surrounding Unicode whitespace, then matched as ASCII
case-insensitive source keys. `UK` maps to `GB`; full-width country names are not folded.
The sorted tuple contains 182 keys including the source's exceptional AC, TA and XK.
It is a snapshot, not an ISO registry or an assignment database.

Codes are stripped of surrounding Unicode whitespace, including line endings. Inside a
code, tabs, Unicode space separators and supported dashes are interchangeable at allowed
separator positions. Runs of those separators are allowed. Leading or trailing dashes,
embedded newlines, controls, punctuation and other scripts' letters are rejected.
Full-width and half-width forms fold to their plain forms; unsupported multi-character
expansions such as U+FFE3 are rejected. Decimal digits recognized by the interpreter's
Unicode database fold to ASCII; superscripts and other compatibility characters do not.
The accepted digit repertoire depends on Python's bundled Unicode version, available as
`unicodedata.unidata_version`. For example, Kawi digits are rejected on Python 3.10 and
3.11 but accepted on Python 3.12 and later. ASCII case folds to uppercase. Normalization
is idempotent and preserves leading zeroes.

The accepted dashes are U+002D, U+00AD, U+FE63, U+2010 through U+2015, U+2212 and
U+30FC (including its half-width form). This is input tolerance, not postal syntax.
Separators can be omitted; their positions follow the canonical layout or explicit
source exceptions for France, Brunei, Anguilla and Oman. Latvia adds `LV-`; Anguilla
and Oman remove optional prefixes; Sweden inserts a space. Argentina accepts legacy
four-digit codes. Ireland restricts routing-key initial letters and excludes O, but
does not check that the complete routing key or individual code is assigned.

## Errors

| Condition | Result |
| --- | --- |
| Known format, malformed code | `is_valid` returns `False`; `normalize` raises `InvalidPostalCodeError` |
| Source country without a format | `UnknownCountryError`, `has_postal_codes is False` |
| Unknown country key | `UnknownCountryError`, `has_postal_codes is None` |
| Non-string country or code | `TypeError` |

Country validation precedes code validation. Both custom errors subclass `ValueError`
and survive copying and pickling. `UnknownCountryError.country` keeps the original
country argument; `InvalidPostalCodeError.country` keeps the resolved key and `.code`
keeps the original code. Directly constructed errors retain the arguments as given.
Their messages omit input values, but attributes and pickles contain them: avoid logging
those indiscriminately. Error constructor annotations specify strings; the constructors
store their inputs without validating postal syntax.

```python
from postalcheck import InvalidPostalCodeError, normalize

try:
    normalize("us", "bad")
except InvalidPostalCodeError as error:
    assert str(error) == "invalid postal code format"
    assert (error.country, error.code) == ("US", "bad")
```

## Command line

`postalcheck COUNTRY [CODE ...]` and `python -m postalcheck COUNTRY [CODE ...]` print
one canonical code per successful input. With no codes, they read UTF-8 stdin (an initial
BOM is ignored), one line at a time, skipping blank lines. Bad input bytes are replaced
and consequently rejected as postal code characters. Success exits 0, any invalid code
or output failure exits 1, and unknown countries or argument errors exit 2. Help exits 0.
Diagnostics go to stderr and omit input; mixed batches continue after invalid codes.
Arguments beginning with `-` can follow `--`. An output pipe closing stops processing
quietly. Output contains ASCII canonical codes and works on non-UTF-8 consoles.

## Upgrade from 0.2.1

Install 1.0.0 over 0.2.1 with the usual package installer. Accepted ordinary strings and
canonical results are unchanged. Catch exception types or read their attributes instead
of parsing messages: input is now omitted from both exception text and CLI diagnostics.
New error pickles refer to the public module; old private-module pickles still load.
String subclasses are read as their underlying values. The
[changelog](https://github.com/JaviLianes8/postalcheck/blob/main/CHANGELOG.md) lists all changes.

## Reproduce checks

Install `.[dev]`. Run `ruff format --check .`, `ruff check .`, `mypy --strict src tests`
and `python -m pytest --basetemp=YOUR_SCRATCH_DIRECTORY`. Every test has a 300-second
timeout. The tests execute the Python blocks in this guide and the README.

Set `POSTALCHECK_UPSTREAM` to a local data directory and run
`python scripts/fetch_upstream.py` to fetch the manifest-pinned external sources.
Tests skip cleanly if these files are absent; changed files fail their hash checks.
The Eircode FAQ uses the manifest's `faq-text-v1` extraction: text nodes inside each
`div[data-sf-field="Content"]` are joined with spaces, Unicode whitespace is collapsed,
and each answer ends with a newline. Scripts, styles, attributes and session fields are
excluded. Size and SHA-256 verify the extracted UTF-8 text, so changed answers still fail.
No external text or dataset is distributed. Facts in the tables are transcribed from
[libaddressinput](https://chromium-i18n.appspot.com/ssl-address/data), with the documented
exceptions. See the source manifest for URLs, dates, sizes, hashes and licensing notes.

Set `POSTALCHECK_E2E=1` to build and install in a temporary environment. Set
`POSTALCHECK_PYPI=1` as well to check the real 0.2.1 release and upgrade it in place.
Set `TEMP` and `TMP` to your scratch directory when build tools should use it too.
