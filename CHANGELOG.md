# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The six public names, signatures and defaults from 0.2.1, the 182 bundled formats,
  Unicode folding, canonical layouts, UK alias and error attributes are retained.
- Python 3.10 through 3.14, zero runtime dependencies, and packaged type information.

### Changed

- Exception messages and CLI diagnostics no longer echo input values. Invalid codes
  report `invalid postal code format`; unknown countries report `unsupported country
  code` or `country does not use postal codes`. CLI usage errors report `invalid
  arguments; use --help`. Attributes retain the original inputs for deliberate access.
- Non-string arguments still raise `TypeError`, but messages omit the type name.
- Error classes identify their public module as `postalcheck` for new pickles. Existing
  0.2.1 pickles still load; new pickles also load in 0.2.1.
- String subclasses use the underlying string value instead of overridden `strip` methods.
- CLI closed-pipe handling uses an in-memory output replacement, retaining exit status 1.

### Fixed

- CLI results are flushed after each successful input, including when stdout is piped
  and stdin remains open. Output failures still exit quietly with status 1.
- Unsupported multi-character width expansions, including U+FFE3 FULLWIDTH MACRON, return
  `False` from `is_valid` and raise `InvalidPostalCodeError` from `normalize`. CLI batches
  reject the input and continue processing subsequent codes.
- Non-string arguments with hostile `__class__` hooks raise the documented safe
  `TypeError` without invoking those hooks; actual string subclasses remain supported.
- The source fetcher verifies deterministic Eircode FAQ answer text, excluding dynamic
  session fields, against the manifest instead of hashing the entire HTML response.
- Documentation clarifies that Unicode digit coverage follows the interpreter's Unicode
  database and that country keys are trimmed of Unicode whitespace before ASCII checks.
- The historical Ireland entry describes routing-key initial letters and the D6W
  exception correctly; complete routing-key assignment is not checked.

### Added

- Runnable public docstrings, a detailed guide, stronger contracts and seeded hostile-input
  tests, installed-wheel and PyPI upgrade checks, and release validation metadata.
- `POSTALCHECK_UPSTREAM` selects a separate local folder for fetched test data.

## [0.2.1] - 2026-10-13

### Changed

- The libaddressinput data and the Eircode routing key page are no longer committed or
  shipped in the sdist: `scripts/fetch_upstream.py` fetches them, checked against
  `tests/upstream/MANIFEST.json`. Every rule is still tested against its own example and
  a hand-written set of routing keys when the files are absent.

## [0.2.0]

### Added

- Rules for all 182 countries and territories that use postal codes (51 before), each
  transcribed from Google libaddressinput and tested against its published examples.
- `example(country)`: a real code in canonical layout, for form placeholders.
- `UnknownCountryError.has_postal_codes`, `False` for the 70 countries and territories
  without postal codes. Both errors keep their inputs (`country`, `code`) and pickle.
- `UK` is read as `GB`.
- Full-width forms, decimal digits recognized by Python's Unicode database, Unicode dashes
  and no-break spaces in the input are folded to ASCII.
- Command line: `postalcheck COUNTRY [CODE ...]` and `python -m postalcheck`, reading
  UTF-8 lines from standard input when no code is given.

### Changed

- Spaces and dashes are allowed only where the country writes a separator:
  `9-0-2-1-0` is no longer a valid US ZIP code. Line breaks and control characters inside
  a code are refused.
- Matching is ASCII only: other scripts' digits are converted first, never matched as is.
- A non-`str` argument raises `TypeError` with a clear message.
- A country key that is not ASCII after surrounding Unicode whitespace is stripped is
  unknown: `str.upper()` no longer turns `ıt` into `IT`.
- Ireland: the last four characters follow the Eircode FAQ (any digit or letter except O),
  which accepts some letters the 0.1.0 table refused (`A65 BBBB`). Routing keys restrict
  the initial letter to those in the 139 published keys, followed by two digits, with
  D6W as an exception. Complete routing-key membership is not checked.

### Fixed

- Latvia: `LV-1073` was refused; bare digits now normalize to that form.
- Vietnam: five-digit codes (in use since 2018) were refused.
- Israel: five-digit codes were refused.
- Netherlands: codes starting with 0 and the letter pairs SA, SD and SS were accepted.
- United Kingdom: postcode areas and inward letters that do not exist were accepted.
- Argentina: CPA codes with I or O as province letter were accepted.

## [0.1.0]

- First release.
- `is_valid` and `normalize` for postal and ZIP codes by ISO country code.
- `supported_countries` listing every country with a rule.
- `UnknownCountryError` and `InvalidPostalCodeError`.
- Bundled per-country table covering AR, AT, AU, BE, BG, BR, CA, CH, CN, CZ, DE,
  DK, EE, ES, FI, FR, GB, GR, HR, HU, ID, IE, IL, IN, IS, IT, JP, KR, LT, LU, LV,
  MX, MY, NL, NO, NZ, PH, PL, PT, RO, RU, SE, SG, SI, SK, TH, TR, UA, US, VN, ZA.
