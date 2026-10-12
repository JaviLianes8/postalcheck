# postalcheck improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [x] Pin the ground truth: libaddressinput data for every country, Eircode routing keys
- [x] Rules for every country with postal codes, checked against the pinned data
- [x] Input normalization: Unicode width, native digits, dashes, separator positions
- [x] Typed API: errors with attributes, `example`, country aliases, no-postal-code countries
- [x] Contracts: pinned examples, regex oracle both ways, README, typing, installed wheel
- [x] Command line: `python -m postalcheck`
- [x] Docs and packaging: README, CHANGELOG, docstrings, metadata
- [ ] Gates: ruff format, ruff check, mypy --strict, pytest
- [ ] Mutation run: removing guarded logic makes the suite fail
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` gives `is_valid`, `normalize` and `supported_countries` over a hand-written table of
51 countries. Compared with the pinned data below:

- Real codes are refused. `LV-1073` (the only form Latvijas Pasts uses) fails because the
  table expects bare digits. Vietnam moved to five-digit codes in 2018 and every one of them
  (`70010`) is refused.
- Codes that cannot exist are accepted. The Dutch table allows `0123 AB` and the letter pairs
  `SA`, `SD` and `SS`, which PostNL never issues. The British pattern accepts any letters
  (`QQ1 1AA`, inward `1CI`). Argentine CPA codes are accepted with `I` and `O` as province
  letter.
- `\d` is matched without `re.ASCII`, so `is_valid("DE", "١٠١١٥")` is true and `normalize`
  returns the Arabic-Indic digits unchanged.
- Separators are dropped wherever they are, so `9-0-2-1-0` is a valid US ZIP code and
  `1 0 1 1 5` a valid German one.
- Full-width input, which Japanese keyboards produce (`１５４－００２３`), is refused, and so are
  codes written with a Unicode dash.
- Only 51 of the 182 countries and territories that have a postal code system are covered.
  There is no way to tell "this country has no postal codes" (Hong Kong, Qatar,
  Panama) from "this is not a country".
- Errors carry no data, there is no example code to show in a form, and `UK` is refused.

## Sources (fetched 2026-10-12)

- Google libaddressinput address metadata, the data set behind Chrome and Android address
  forms, https://chromium-i18n.appspot.com/ssl-address/data/<CC> for each of the 252 country
  keys listed at https://chromium-i18n.appspot.com/ssl-address/data. Each response body is
  committed unchanged, one per line, in `tests/data/libaddressinput.jsonl`
  (sha256 f2417db82d928fe0b19c557ca97fd321f6498dfc775d6338e990f1b1981bc112). The `zip`
  field is the format regular expression, `zipex` lists real codes; 182 countries have one.
- Eircode, https://www.eircode.ie/what-is-eircode and https://www.eircode.ie/faqs: a routing
  key of three characters and a unique identifier of four, and "the number zero is included
  in the character set used for Eircodes, but the letter 'O' is not".
- The 139 Eircode routing keys, Wikipedia "List of Eircode routing areas in Ireland",
  revision 1348214965 (2026-04-11),
  https://en.wikipedia.org/w/index.php?oldid=1348214965&action=raw, committed unchanged as
  `tests/data/eircode-routing-keys.wiki`
  (sha256 e5d46fe105832ebda145cc9bb538c4b5a041332d1587f7fbc26634e7d1e7dcbb).

Invalid samples in the tests are written by hand and labelled as such.

## Ranked improvements

1. **Every country with postal codes.** One rule per libaddressinput entry (182), each a
   pattern over the compact code plus its canonical layout taken from the `zipex` examples.
   Fixes the wrong 0.1.0 rules (LV, VN, NL, GB, AR, IL).
2. **Proven against the pinned data.** Every `zipex` code validates and normalizes to itself.
   A sampler walks each upstream regular expression: every string it accepts, we accept. A
   second sampler walks our patterns: every normal form we produce, upstream accepts. The
   few deliberate differences are listed in one place and tested.
3. **Input normalization.** NFKC (full-width digits and letters), native decimal digits to
   ASCII, every Unicode dash and space as a separator, ASCII-only matching. Separators are
   optional, interchangeable, and allowed only where the canonical form has one (or where
   upstream allows one, such as France's `75 008`).
4. **Typed API.** `InvalidPostalCodeError` and `UnknownCountryError` keep `country` and
   `code` and survive pickling; `UnknownCountryError.has_postal_codes` tells a real country
   without a postal system from an unknown code; `example(country)` returns a real code for
   form placeholders; `UK` is read as `GB`.
5. **Contracts.** README examples executed, public types checked with mypy, `__all__` pinned,
   installed-wheel end-to-end test, every guarded branch proven by a mutation run.
6. **Command line.** `python -m postalcheck CC CODE...` (or lines on stdin) prints the normal
   form of each code and exits 1 if any is invalid. Useful to clean a column in a pipeline.
7. **Docs and packaging.** Country table generated from the rules and checked by a test,
   CHANGELOG for 0.2.0, classifiers, sdist without planning notes, gate over the whole tree.

## Out of scope

- Checking that a code is assigned (exists in the operator's database). That needs the
  national address files, which are large, licensed and change monthly. This library checks
  the format.
- Matching a code against a state or city (libaddressinput's `sub_zips`).
- Stripping a country prefix such as `D-10115` or `F-75008`: the old European habit clashes
  with real codes (`DE1 1AA` is a Derby postcode), so it is not guessed.
